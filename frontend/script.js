// Use the current hostname to work across the network
const API_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port || (window.location.protocol === 'https:' ? 443 : 80)}/chat/`;

const inputEl  = document.getElementById("user-input");
const sendBtn  = document.getElementById("send-btn");
const micBtn   = document.getElementById("mic-btn");

// ── Voice recording ────────────────────────────────────────────────────────────
let recognition     = null;
let isRecording     = false;
let finalTranscript = "";   // built up from final recognition results

const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechAPI) {
    recognition = new SpeechAPI();
    recognition.continuous     = false;  // single utterance; onend fires after silence
    recognition.interimResults = true;   // show live preview while speaking
    recognition.lang           = "en-US";

    // Live preview while user speaks
    recognition.onresult = (event) => {
        finalTranscript = "";
        let interim = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interim += event.results[i][0].transcript;
            }
        }
        // Show interim text while speaking; final text once confirmed
        inputEl.value = finalTranscript || interim;
    };

    // onerror: just log; onend fires right after and handles UI reset
    recognition.onerror = (e) => {
        if (e.error === "not-allowed") {
            addMessage("bot", "Microphone access denied. Please allow microphone permissions in your browser and try again.");
        }
    };

    // onend fires in ALL cases: natural silence, manual stop, or error
    // This is the single place that resets UI and decides whether to send
    recognition.onend = () => {
        _resetMicUI();
        if (finalTranscript.trim()) {
            inputEl.value = finalTranscript.trim();
            sendMessage();
        }
    };
} else {
    micBtn.style.display = "none";
}

function toggleRecording() {
    if (isRecording) {
        // User clicked to stop early — keep whatever was heard and send
        finalTranscript = inputEl.value.trim();
        recognition.stop();     // triggers onend → _resetMicUI + sendMessage
    } else {
        startRecording();
    }
}

function startRecording() {
    if (!recognition || isRecording) return;
    isRecording     = true;
    finalTranscript = "";
    inputEl.value   = "";
    inputEl.placeholder = "Listening…";
    micBtn.classList.add("recording");
    try {
        recognition.start();
    } catch (_) {
        _resetMicUI();  // e.g. already started — just reset cleanly
    }
}

// Only resets UI — never calls recognition.stop() to avoid circular triggers
function _resetMicUI() {
    isRecording = false;
    micBtn.classList.remove("recording");
    inputEl.placeholder = "Type your message…";
}

// ── Chat core ──────────────────────────────────────────────────────────────────
inputEl.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function setLoading(on) {
    inputEl.disabled = on;
    sendBtn.disabled = on;
    if (micBtn) micBtn.disabled = on;
}

async function sendMessage() {
    const message = inputEl.value.trim();
    if (!message) return;

    addMessage("user", message);
    inputEl.value = "";
    setLoading(true);
    showTyping();

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        if (!res.ok) throw new Error(`Server error: ${res.status}`);

        const data = await res.json();

        setTimeout(() => {
            removeTyping();
            addMessage("bot", data.response);
            setLoading(false);
            inputEl.focus();
        }, 800);
    } catch {
        removeTyping();
        addMessage("bot", "Sorry, I couldn't connect. Please try again.");
        setLoading(false);
    }
}

function addMessage(role, text) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = role === "user" ? "user-message" : "bot-message";
    // Render **bold** markdown from bot
    msg.innerHTML = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ── Typing indicator ───────────────────────────────────────────────────────────
function showTyping() {
    const chatBox = document.getElementById("chat-box");
    const bubble = document.createElement("div");
    bubble.id = "typing";
    bubble.className = "typing-indicator";
    bubble.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById("typing");
    if (el) el.remove();
}

// ── Quick suggestion buttons ───────────────────────────────────────────────────
function quickMsg(text) {
    inputEl.value = text;
    sendMessage();
}
