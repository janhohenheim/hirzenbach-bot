from typing import Set, Dict, List
from dataclasses import dataclass, field
import pickle


@dataclass(frozen=False)
class Data:
    sticker_pool: Set[str] = field(default_factory=set)
    adding_sticker: bool = False
    subscribers: Set[int] = field(default_factory=set)
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
            _ensure_attr(data, "subscribers", set())
            _ensure_attr(data, "morning_subscribers", set())
            _ensure_attr(data, "memory", dict())
            return data

    def write(self) -> None:
        with open("data.pickle", "wb") as f:
            pickle.dump(self, f)


def _ensure_attr(obj, attr, default):
    if not hasattr(obj, attr):
        setattr(obj, attr, default)
