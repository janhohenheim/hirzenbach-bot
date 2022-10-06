from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    telegram_token: str
    openai_token: str
    openai_org: str

    def read() -> "Env":
        load_dotenv()
        return Env(
            telegram_token=os.environ["TELEGRAM_TOKEN"],
            openai_token=os.environ["OPENAI_TOKEN"],
            openai_org=os.environ["OPENAI_ORG"],
        )
