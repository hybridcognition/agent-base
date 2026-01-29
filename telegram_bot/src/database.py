"""SQLite database operations for message queue and processing lock."""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Get SQLite database connection.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Database connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """Initialize database with required tables.

    Creates messages and processing_lock tables if they don't exist.

    Args:
        db_path: Path to SQLite database file
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Messages table for incoming/outgoing message queue
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_id INTEGER,
            username TEXT,
            message_id INTEGER,
            text TEXT,
            voice_file_path TEXT,
            voice_transcription TEXT,
            direction TEXT NOT NULL,
            processed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Processing lock table (singleton pattern)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_lock (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            is_locked BOOLEAN DEFAULT 0,
            locked_at TIMESTAMP
        )
    """)

    # Initialize lock row if doesn't exist
    cursor.execute("""
        INSERT OR IGNORE INTO processing_lock (id, is_locked)
        VALUES (1, 0)
    """)

    conn.commit()
    conn.close()


def add_incoming_message(
    db_path: str,
    chat_id: int,
    user_id: int,
    username: str,
    message_id: int,
    text: Optional[str] = None,
    voice_file_path: Optional[str] = None,
    voice_transcription: Optional[str] = None
) -> int:
    """Add incoming message to database.

    Args:
        db_path: Path to database
        chat_id: Telegram chat ID
        user_id: Telegram user ID
        username: Telegram username
        message_id: Telegram message ID
        text: Message text (optional for voice)
        voice_file_path: Path to voice file (optional)
        voice_transcription: Voice transcription (optional)

    Returns:
        Database row ID of inserted message
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (
            chat_id, user_id, username, message_id, text,
            voice_file_path, voice_transcription, direction, processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'incoming', 0)
    """, (chat_id, user_id, username, message_id, text,
          voice_file_path, voice_transcription))

    message_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return message_id


def add_outgoing_message(db_path: str, chat_id: int, text: str) -> int:
    """Add outgoing message to database.

    Args:
        db_path: Path to database
        chat_id: Telegram chat ID
        text: Message text

    Returns:
        Database row ID of inserted message
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (chat_id, text, direction)
        VALUES (?, ?, 'outgoing')
    """, (chat_id, text))

    message_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return message_id


def get_unprocessed_messages(db_path: str) -> List[Dict]:
    """Get all unprocessed incoming messages.

    Args:
        db_path: Path to database

    Returns:
        List of message dictionaries ordered by created_at
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, chat_id, user_id, username, message_id, text,
               voice_file_path, voice_transcription, created_at
        FROM messages
        WHERE direction = 'incoming' AND processed = 0
        ORDER BY created_at ASC
    """)

    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'chat_id': row[1],
            'user_id': row[2],
            'username': row[3],
            'message_id': row[4],
            'text': row[5],
            'voice_file_path': row[6],
            'voice_transcription': row[7],
            'created_at': row[8]
        })

    conn.close()
    return messages


def mark_messages_processed(db_path: str, message_ids: List[int]) -> None:
    """Mark messages as processed.

    Args:
        db_path: Path to database
        message_ids: List of message IDs to mark as processed
    """
    if not message_ids:
        return

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    placeholders = ','.join('?' * len(message_ids))
    cursor.execute(f"""
        UPDATE messages
        SET processed = 1
        WHERE id IN ({placeholders})
    """, message_ids)

    conn.commit()
    conn.close()


def acquire_lock(db_path: str) -> bool:
    """Attempt to acquire processing lock.

    Args:
        db_path: Path to database

    Returns:
        True if lock acquired, False if already locked
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Check if already locked
    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()

    if row and row[0] == 1:
        conn.close()
        return False

    # Acquire lock
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE processing_lock
        SET is_locked = 1, locked_at = ?
        WHERE id = 1
    """, (now,))

    conn.commit()
    conn.close()

    return True


def release_lock(db_path: str) -> None:
    """Release processing lock.

    Args:
        db_path: Path to database
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE processing_lock
        SET is_locked = 0, locked_at = NULL
        WHERE id = 1
    """)

    conn.commit()
    conn.close()


def is_locked(db_path: str) -> bool:
    """Check if processing lock is held.

    Args:
        db_path: Path to database

    Returns:
        True if locked, False otherwise
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()

    conn.close()

    if row and row[0] == 1:
        return True
    return False
