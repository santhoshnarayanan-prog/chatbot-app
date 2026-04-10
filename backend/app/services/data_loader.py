import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"
_docs_cache: str | None = None


def load_local_docs() -> str:
    global _docs_cache
    if _docs_cache is not None:
        return _docs_cache

    if not _DATA_DIR.exists():
        logger.warning("Data directory not found: %s", _DATA_DIR)
        _docs_cache = ""
        return _docs_cache

    parts: list[str] = []
    for txt_file in sorted(_DATA_DIR.glob("*.txt")):
        try:
            parts.append(txt_file.read_text(encoding="utf-8"))
        except OSError as e:
            logger.warning("Could not read %s: %s", txt_file, e)

    _docs_cache = "\n".join(parts)
    logger.info("Loaded %d doc file(s) from %s", len(parts), _DATA_DIR)
    return _docs_cache
