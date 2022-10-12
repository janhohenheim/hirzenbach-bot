import openai
from env import Env

_ENGINE = "text-curie-001"
# OpenAI Codex is free during private beta; let's use the best model
_CODE_ENGINE = "code-cushman-001"


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
    return _get_first_nonempty_completion(completion)


def complete_code_prompt(prompt: str) -> str:
    completion = openai.Completion.create(
        engine=_CODE_ENGINE,
        prompt=prompt,
        max_tokens=2048,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return _get_first_nonempty_completion(completion)


def _get_first_nonempty_completion(completion: openai.Completion) -> str:
    for choice in completion.choices:
        text = choice.text.strip()
        if text != "":
            return text
    return ""
