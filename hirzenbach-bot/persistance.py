from typing import Set, Dict, List, Optional
from dataclasses import dataclass, field
import pickle
import sqlite3

_SQLITE_DATABASE = 'hirzenbach_bot.sqlite3'
_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS stickers
    ( file_id TEXT PRIMARY KEY ON CONFLICT REPLACE);
CREATE TABLE IF NOT EXISTS sticker_subscribers
    ( chat_id INTEGER PRIMARY KEY ON CONFLICT REPLACE);
CREATE TABLE IF NOT EXISTS morning_subscribers
    ( chat_id INTEGER PRIMARY KEY ON CONFLICT REPLACE);
CREATE TABLE IF NOT EXISTS memory
    ( chat_id INTEGER
    , message TEXT
    );
CREATE TABLE IF NOT EXISTS sticker_adders
    ( chat_id INTEGER PRIMARY KEY ON CONFLICT REPLACE);
"""


def init_database() -> None:
    connection = _connect()
    connection.executescript(_SQLITE_SCHEMA)


def get_stickers() -> List[str]:
    with _connect() as connection:
        return [sticker_id for (sticker_id,) in connection.execute("SELECT file_id FROM stickers").fetchall()]


def add_sticker(sticker_id: str) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO stickers (file_id) VALUES (?)", (sticker_id,))


def subscribe_stickers(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO sticker_subscribers (chat_id) VALUES (?)", (chat_id,))


def unsubscribe_stickers(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM sticker_subscribers WHERE chat_id = ?", (chat_id,))


def get_sticker_subscribers() -> List[int]:
    with _connect() as connection:
        return [chat_id for (chat_id,) in connection.execute("SELECT chat_id FROM sticker_subscribers").fetchall()]


def subscribe_morning(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO morning_subscribers (chat_id) VALUES (?)", (chat_id,))


def unsubscribe_morning(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM morning_subscribers WHERE chat_id = ?", (chat_id,))


def get_morning_subscribers() -> List[int]:
    with _connect() as connection:
        return [chat_id for (chat_id,) in connection.execute("SELECT chat_id FROM morning_subscribers").fetchall()]


def append_to_memory(chat_id: int, message: str, limit: Optional[int] = None):
    with _connect() as connection:
        connection.execute("INSERT INTO memory (chat_id, message) VALUES (?, ?)", (chat_id, message))
        if limit is not None:
            connection.execute("DELETE FROM memory WHERE rowid IN ("
                               "    SELECT rowid FROM memory WHERE chat_id = ?"
                               "    ORDER BY rowid DESC LIMIT -1 OFFSET ?)", (chat_id, limit))


def get_memory(chat_id: int) -> List[str]:
    with _connect() as connection:
        return [message for (message,) in connection.execute("SELECT message FROM memory WHERE chat_id = ?", (chat_id,))]


def remove_from_memory(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM memory WHERE chat_id = ?", (chat_id,))


def enable_adding_stickers(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO sticker_adders (chat_id) VALUES (?)", (chat_id,))


def disable_adding_stickers(chat_id: int) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM sticker_adders WHERE chat_id = ?", (chat_id,))


def is_adding_stickers(chat_id: int) -> bool:
    with _connect() as connection:
        result, = connection.execute("SELECT count(1) FROM sticker_adders WHERE chat_id = ?", (chat_id,)).fetchone()
        return result >= 1


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(_SQLITE_DATABASE)


@dataclass(frozen=False)
class Data:
    sticker_pool: Set[str] = field(default_factory=set)
    adding_sticker: bool = False
    sticker_subscribers: Set[int] = field(default_factory=set)
    morning_subscribers: Set[int] = field(default_factory=set)
    memory: Dict[int, List[str]] = field(default_factory=dict)

    def init() -> None:
        try:
            Data.read()
        except FileNotFoundError:
            Data.write(Data())

    def read() -> "Data":
        with open("data.pickle", "rb") as f:
            data = pickle.load(f)
            _ensure_attr(data, "sticker_pool", set())
            _ensure_attr(data, "adding_sticker", False)
            _ensure_attr(data, "sticker_subscribers", set())
            _ensure_attr(data, "morning_subscribers", set())
            _ensure_attr(data, "memory", dict())
            return data

    def write(self) -> None:
        with open("data.pickle", "wb") as f:
            pickle.dump(self, f)


def _ensure_attr(obj, attr, default):
    if not hasattr(obj, attr):
        setattr(obj, attr, default)
