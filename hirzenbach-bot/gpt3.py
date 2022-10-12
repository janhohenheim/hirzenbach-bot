import imp
import openai
import os
from env import Env

_ENGINE = "text-curie-001"
# OpenAI Codex is free during private beta; let's use the best model
_CODE_ENGINE = "code-davin-002"

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
    return completion.choices[0].text.strip()


def complete_code_prompt(prompt: str) -> str:
    completion = openai.Completion.create(
        engine=_CODE_ENGINE,
        prompt=prompt,
        max_tokens=2048,
    )
    return completion.choices[0].text.strip()
