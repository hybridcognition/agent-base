"""Access control via whitelist of allowed chat IDs."""
import os
from typing import Set


_allowed_ids: Set[int] = None


def load_whitelist() -> Set[int]:
    """Load allowed chat IDs from environment variable.

    Returns:
        Set of allowed chat IDs

    Raises:
        ValueError: If ALLOWED_CHAT_IDS is empty or invalid
    """
    global _allowed_ids

    if _allowed_ids is not None:
        return _allowed_ids

    allowed_str = os.getenv("ALLOWED_CHAT_IDS", "")

    if not allowed_str:
        # Secure by default - deny if whitelist empty
        raise ValueError("ALLOWED_CHAT_IDS environment variable is empty")

    try:
        _allowed_ids = {int(id.strip()) for id in allowed_str.split(",")}
    except ValueError as e:
        raise ValueError(f"Invalid chat ID in ALLOWED_CHAT_IDS: {e}")

    return _allowed_ids


def is_whitelisted(chat_id: int) -> bool:
    """Check if chat ID is whitelisted.

    Args:
        chat_id: Telegram chat ID to check

    Returns:
        True if whitelisted, False otherwise
    """
    try:
        whitelist = load_whitelist()
        return chat_id in whitelist
    except ValueError:
        # If whitelist loading fails, deny access
        return False
