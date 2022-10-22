from dataclasses import dataclass, field
from typing import Set, Dict, List
import pickle
from persistence import init_database, add_sticker, subscribe_morning, subscribe_stickers, append_to_memory


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


def migrate():
    data = Data.read()
    _migrate_stickers(data)
    _migrate_sticker_subscribers(data)
    _migrate_morning_subscribers(data)
    _migrate_memory(data)


def _migrate_stickers(data: Data):
    for sticker in data.sticker_pool:
        add_sticker(sticker)


def _migrate_sticker_subscribers(data: Data):
    for chat_id in data.sticker_subscribers:
        subscribe_stickers(chat_id)


def _migrate_morning_subscribers(data: Data):
    for chat_id in data.morning_subscribers:
        subscribe_morning(chat_id)


def _migrate_memory(data: Data):
    for chat_id, messages in data.memory.items():
        for message in messages:
            append_to_memory(chat_id, message)


if __name__ == '__main__':
    init_database()
    migrate()
