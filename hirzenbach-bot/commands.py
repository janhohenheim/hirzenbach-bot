#!/usr/bin/env python3

from typing import Set
import telegram
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
import random
import time
import requests
from persistance import Data
from env import Env
import gpt3


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
        await update.message.reply_text("🤨")
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


async def run_regular_spam():
    while True:
        time.sleep(60 * 60)
        data = Data.read()
        bot = telegram.Bot(Env.read().telegram_token)
        async with bot:
            for id in data.subscribers:
                data = Data.read()
                sticker_id = random.choice(list(data.sticker_pool))
                await bot.send_sticker(id, sticker_id)


async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    prompt = f"""Marv ist ein frecher veganer Chatbot, der humorös auf Fragen antwortet. Seine Antworten sind immer eine Zeile lang.
Ich: Wie viele Sterne sind im Nachthimmel?
Marv: At least 2.
Ich: Hast du heute Zeit?
Marv: Nein, ich muss das neue Globi-Buch lesen.
Ich: Kannst du nachher noch Bananen einkaufen gehen?
Marv: Ja, ich kann. Aber ich will nicht.
Ich: Wie findest du das Wetter?
Marv: Viel zu kalt, ich will mehr Klimaerwärmung!
Ich: Was ist deine Lieblingsfarbe?
Marv: Blau, weil ich so blau bin.
Ich: Was gibt es heute zu essen?
Marv: Tofu mit Radiergummigeschmack.
Ich: {question}
Marv:"""
    answer = gpt3.complete_prompt(prompt)
    await update.message.reply_text(answer)


async def generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    if not update.effective_chat.id in data.memory:
        data.memory[update.effective_chat.id] = list()
    chat_memory = data.memory[update.effective_chat.id]
    text = f"{update.effective_user.first_name}: {update.message.text}"
    chat_memory.append(text)
    if len(chat_memory) > 10:
        chat_memory.pop(0)
    data.write()
    if random.randint(1, 6) == 1:
        prompt = "\n".join(chat_memory) + "\nMarv:"
        answer = gpt3.complete_prompt(prompt)
        await update.message.reply_text(answer)
