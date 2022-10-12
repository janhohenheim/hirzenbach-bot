#!/usr/bin/env python3

from typing import List
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
import random
import gpt3
import requests
from persistance import Data

# Arbitrary, but it seems a gender neutral name gives less mechanical responses
# than the real name or a typical bot name like "Marv"
BOT_NAME = "Kim"


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Hi {update.effective_user.first_name}! My developer was too lazy to write down any help :)"
    )


async def there_there(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"There there *pats head*")
    sticker = random.choice(
        [
            "CAACAgIAAxkBAAEYu_5jPf5WYDTn3Jc5hRqRw4HvtVTMGgACMQEAAlKJkSNy74zuyFRhcyoE",
            "CAACAgIAAxkBAAEYvAABYz3-bjX-Po33KiqNVfMqZPNnxfQAAuwAA_cCyA805OGp51WLlyoE",
        ]
    )
    await update.message.reply_sticker(sticker)


async def start_add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.adding_sticker = True
    data.write()
    await update.message.reply_text("Alright, send the stickers!")


async def stop_add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.adding_sticker = False
    data.write()
    await update.message.reply_text(
        "Stopped adding stickers. You can start again via /add_sticker"
    )


async def add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    if not data.adding_sticker:
        return

    data.sticker_pool.add(update.message.sticker.file_id)
    data.write()
    await update.message.reply_text("Added sticker! You can stop via /stop_add_sticker")


async def sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    id = random.choice(list(data.sticker_pool))
    await update.message.reply_sticker(id)


async def subscribe_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.sticker_subscribers.add(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Added to subscribers of scheduled sticker spam. You can unsubscribe via /unsubscribe_sticker"
    )


async def subscribe_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.morning_subscribers.add(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Added to subscribers of scheduled good morning messages. You can unsubscribe via /unsubscribe_morning"
    )


async def unsubscribe_sticker(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    data = Data.read()
    data.sticker_subscribers.remove(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Removed from subscribers of scheduled sticker spam. Subscribe again via /subscribe_sticker"
    )


async def unsubscribe_morning(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    data = Data.read()
    data.morning_subscribers.remove(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Removed from subscribers of scheduled good morning messages. Subscribe again via /subscribe_morning"
    )


async def inspire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = requests.get("https://inspirobot.me/api?generate=true")
    if response.status_code != 200:
        await update.message.reply_text("Something went wrong :(")
        return
    link = response.text
    await update.message.reply_photo(link)


async def generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    if not update.effective_chat.id in data.memory:
        data.memory[update.effective_chat.id] = list()
    chat_memory = _append_to_memory(
        update.effective_chat.id,
        update.effective_user.first_name,
        update.effective_message.text,
    )

    reply_to_message = update.effective_message.reply_to_message
    is_reply_to_me = (
        reply_to_message is not None and reply_to_message.from_user.id == context.bot.id
    )
    is_addressing_me = context.bot.name in update.effective_message.text

    if random.randint(1, 6) == 1 or is_reply_to_me or is_addressing_me:
        prompt = (
            "\n".join(
                message.replace(context.bot.name, f"@{BOT_NAME}")
                for message in chat_memory
            )
            + f"\n{BOT_NAME}:"
        )
        answer = gpt3.complete_prompt(prompt)
        _append_to_memory(update.effective_chat.id, BOT_NAME, answer)
        if answer is not None and answer != "":
            await update.message.reply_text(answer)


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coding_request = update.effective_message.text.replace("/code ", "").strip()
    if coding_request == "":
        await update.message.reply_markdown(
            "Please specify a coding request, e.g. `/code a single function implementing fizzbuzz`"
        )
        return
    prompt = f'"""\nPython 3\n{coding_request}.\nThe code is implemented using modern, clean, functional programming.\nIt is readable and concise. There are not too many imports or functions.\n"""'
    answer = gpt3.complete_code_prompt(prompt)
    if answer is not None and answer != "":
        formatted_code = f"```\n{answer}\n```"
        await update.message.reply_markdown(formatted_code)


def _append_to_memory(chat: int, user: str, text: str) -> List[str]:
    data = Data.read()
    if not chat in data.memory:
        data.memory[chat] = list()
    chat_memory = data.memory[chat]
    text = f"{user}: {text}"
    chat_memory.append(text)
    while len(chat_memory) > 10:
        chat_memory.pop(0)
    data.write()
    return chat_memory
