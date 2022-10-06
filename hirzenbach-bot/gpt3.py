import imp
import openai
import os
from env import Env

_ENGINE = "text-curie-001"


def setup_openai() -> None:
    env = Env.read()
    openai.api_key = env.openai_token
    openai.organization = env.openai_org


def complete_prompt(prompt: str) -> str:
    completion = openai.Completion.create(
        engine=_ENGINE,
        prompt=prompt,
        max_tokens=128,
        stop=["\n"],
    )
    return completion.choices[0].text
