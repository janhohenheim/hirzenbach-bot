from typing import Set
from dataclasses import dataclass, field
import pickle


@dataclass(frozen=False)
class Data:
    sticker_pool: Set[str] = field(default_factory=set)
    adding_sticker: bool = False
    subscribers: Set[int] = field(default_factory=set)

    def init() -> None:
        try:
            Data.read()
        except FileNotFoundError:
            Data.write(Data())

    def read() -> "Data":
        with open("data.pickle", "rb") as f:
            return pickle.load(f)

    def write(self) -> None:
        with open("data.pickle", "wb") as f:
            pickle.dump(self, f)
