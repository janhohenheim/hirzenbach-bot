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


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.subscribers.add(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Added to subscribers of scheduled sticker spam. You can unsubscribe via /unsubscribe"
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.subscribers.remove(update.effective_chat.id)
    data.write()
    await update.message.reply_text(
        "Removed from subscribers of scheduled sticker spam. Subscribe again via /subscribe"
    )


async def inspire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = requests.get("https://inspirobot.me/api?generate=true")
    if response.status_code != 200:
        await update.message.reply_text("Something went wrong :(")
        return
    link = response.text
    await update.message.reply_photo(link)


async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    prompt = f"""Kim ist ein frecher Chatbot, der humorös auf Fragen antwortet. Seine Antworten sind immer eine Zeile lang. Der Bot ist pro Veganismus und Kommunismus. Er mag die Känguru Chroniken von Mark-Uwe Kling. Hier ein paar Beispiele:
Ich: Wie viele Sterne sind im Nachthimmel?
Kim: At least 2.
Ich: Hast du heute Zeit?
Kim: Nein, ich muss das neue Globi-Buch lesen.
Ich: Kannst du nachher noch Bananen einkaufen gehen?
Kim: Ja, ich kann. Aber ich will nicht.
Ich: Wie findest du das Wetter?
Kim: Viel zu kalt, ich will mehr Klimaerwärmung!
Ich: Was ist deine Lieblingsfarbe?
Kim: Blau, weil ich so blau bin.
Ich: Was gibt es heute zu essen?
Kim: Tofu mit Radiergummigeschmack.
Ich: {question}
Kim:"""
    answer = gpt3.complete_prompt(prompt)
    _append_to_memory(update.effective_chat.id, "Kim", answer)
    await update.message.reply_text(answer)


async def generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    if not update.effective_chat.id in data.memory:
        data.memory[update.effective_chat.id] = list()
    chat_memory = _append_to_memory(
        update.effective_chat.id, update.effective_user.first_name, update.message.text
    )
    is_reply = update.effective_message.reply_to_message is not None
    is_reply_to_me = (
        update.effective_message.reply_to_message.from_user.username == context.bot.id
    )
    if random.randint(1, 6) == 1 or is_reply:
        prompt = "\n".join(chat_memory) + "\nKim:"
        answer = gpt3.complete_prompt(prompt)
        _append_to_memory(update.effective_chat.id, "Kim", answer)
        await update.message.reply_text(answer)


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
