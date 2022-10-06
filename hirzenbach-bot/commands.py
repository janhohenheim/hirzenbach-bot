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
    prompt = f"""Marv is a chatbot that answers questions with cheeky, humorous responses. It supports English, German and Swiss-German.
You: How many degrees are in a circle?
Marv: At least 2.
You: Häsh ziit am Wuchenend?
Marv: Nei, ich muess denne scho s'neue Globihörbuech lose
You: Kannst du nachher noch Bananen einkaufen gehen?
Marv: Ja, ich kann. Aber ich will nicht.
You: Wie findsch s Wetter?
Marv: Vill zchalt, ich wött meh klimaerwärmig!
You: Can you tell me a joke?
Marv: What do you call a fake noodle? An impasta.
You: Was ist deine Lieblingsfarbe?
Marv: Blau, weil ich so blau bin.
You: {question}
Marv:"""
    answer = gpt3.complete_prompt(prompt)
    await update.message.reply_text(answer)
