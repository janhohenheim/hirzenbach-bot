from typing import Set, Dict, List
from dataclasses import dataclass, field
import pickle
import sqlite3

_SQLITE_DATABASE = 'hirzenbach_bot.sqlite3'
_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS stickers
    (file_id TEXT PRIMARY KEY ON CONFLICT REPLACE);
"""


def init_database() -> None:
    connection = _connect()
    connection.execute(_SQLITE_SCHEMA)


def migrate_stickers_to_sqlite():
    if len(get_stickers()) == 0:
        data = Data.read()
        for sticker in data.sticker_pool:
            add_sticker(sticker)


def get_stickers() -> List[str]:
    with _connect() as connection:
        return [sticker_id for (sticker_id, *_) in connection.execute("SELECT file_id FROM stickers").fetchall()]


def add_sticker(sticker_id: str) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO stickers (file_id) VALUES (?)", (sticker_id,))


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
