import asyncio
import logging
import re

from dotenv import load_dotenv

from app.services.ai_provider import get_provider
from app.services.data_loader import load_local_docs
from app.services.email_service import send_email
from app.services.knowledge_service import query_knowledge

load_dotenv()

logger = logging.getLogger(__name__)

_provider = get_provider()
_MAX_HISTORY = 20

conversation_history: list[dict] = []

# ── Contact collection state ───────────────────────────────────────────────────
# _contact_step: -1 = idle, 0 = awaiting business name, 1 = awaiting email, 2 = awaiting phone
_contact_step: int = -1
_contact_info: dict = {}

_CONTACT_QUESTIONS = [
    "Sure! To send your request to our team, could you share your **business or company name**?",
    "Got it! And your **contact email address**?",
    "Almost done — what is your **phone number**?",
]

# Phrases that start the contact-collection flow (must be more explicit to avoid false triggers)
_FINALIZE_TRIGGERS = {"send", "submit", "contact", "reach out", "get in touch", "email me", "call me"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _trim_history() -> None:
    global conversation_history
    if len(conversation_history) > _MAX_HISTORY:
        conversation_history = conversation_history[-_MAX_HISTORY:]


def _build_messages(docs: str, knowledge_context: str = "") -> list[dict]:
    knowledge_block = (
        f"\n\nKnowledge Base:\n{knowledge_context}" if knowledge_context else ""
    )
    system_prompt = (
        "You are LUNA, a professional MCUBE support assistant.\n"
        "- Answer based on the Knowledge Base when relevant; otherwise use your general knowledge\n"
        "- Keep responses concise and friendly\n"
        "- Be polite and human-like\n\n"
        f"Company Info:\n{docs}"
        f"{knowledge_block}"
    )
    return [{"role": "system", "content": system_prompt}] + conversation_history


def _extract_email(text: str) -> str:
    match = re.search(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", text)
    return match.group(0) if match else text.strip()


def _extract_phone(text: str) -> str:
    match = re.search(r"[\+]?[\d\s\-\(\)]{7,15}", text)
    return match.group(0).strip() if match else text.strip()


# ── Email trigger ──────────────────────────────────────────────────────────────

async def _handle_email_trigger() -> str:
    logger.info("Sending support email with contact info: %s", _contact_info)

    summary_messages = [
        {
            "role": "system",
            "content": "Summarize this customer conversation in 3 short professional bullet points.",
        }
    ] + conversation_history

    summary = await _provider.complete(summary_messages)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: send_email(summary=summary, contact_info=_contact_info),
    )
    return (
        "All done! I've sent your request along with your contact details to our team. "
        "Someone will reach out to you shortly."
    )


# ── Main entry point ───────────────────────────────────────────────────────────

async def get_ai_response(message: str) -> str:
    global _contact_step, _contact_info

    # ── Contact collection state machine ──────────────────────────────────────
    if _contact_step == 0:
        _contact_info["business_name"] = message.strip()
        _contact_step = 1
        return _CONTACT_QUESTIONS[1]

    if _contact_step == 1:
        _contact_info["email"] = _extract_email(message)
        _contact_step = 2
        return _CONTACT_QUESTIONS[2]

    if _contact_step == 2:
        _contact_info["phone"] = _extract_phone(message)
        _contact_step = -1
        return await _handle_email_trigger()

    # ── Finalize trigger ───────────────────────────────────────────────────────
    message_lower = message.strip().lower()
    if any(trigger in message_lower for trigger in _FINALIZE_TRIGGERS):
        _contact_step = 0
        _contact_info = {}
        return _CONTACT_QUESTIONS[0]

    # ── Normal AI flow ─────────────────────────────────────────────────────────
    docs = load_local_docs()

    # Retrieve relevant knowledge base context for this message
    loop = asyncio.get_event_loop()
    knowledge_context = await loop.run_in_executor(None, lambda: query_knowledge(message))

    conversation_history.append({"role": "user", "content": message})
    _trim_history()

    ai_reply = await _provider.complete(_build_messages(docs, knowledge_context))

    conversation_history.append({"role": "assistant", "content": ai_reply})
    _trim_history()

    logger.info("AI reply generated (%d chars)", len(ai_reply))
    return ai_reply
