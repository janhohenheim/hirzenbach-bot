#!/usr/bin/env python3

import asyncio
from typing import Set
import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import random
from dataclasses import dataclass, field
import pickle
import time
from threading import Thread
from dotenv import load_dotenv
import os


@dataclass(frozen=False)
class Data:
    sticker_pool: Set[str] = field(default_factory=set)
    adding_sticker: bool = False
    subscribers: Set[int] = field(default_factory=set)

    def read() -> "Data":
        with open("data.pickle", "rb") as f:
            return pickle.load(f)

    def write(self) -> None:
        with open("data.pickle", "wb") as f:
            pickle.dump(self, f)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def there_there(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"There there *pats head*")


async def start_add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.adding_sticker = True
    data.write()
    await update.message.reply_text("Alright, send the stickers!")


async def stop_add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.adding_sticker = False
    data.write()
    await update.message.reply_text("Stopped adding stickers")


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
    await update.message.reply_text("Added to subscribers")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = Data.read()
    data.subscribers.remove(update.effective_user.id)
    data.write()
    await update.message.reply_text("Removed from subscribers")


def init_pickle() -> None:
    try:
        Data.read()
    except FileNotFoundError:
        Data.write(Data())


async def run_regular_spam():
    while True:
        data = Data.read()
        bot = telegram.Bot(get_token())
        async with bot:
            for id in data.subscribers:
                data = Data.read()
                sticker_id = random.choice(list(data.sticker_pool))
                await bot.send_message(
                    id,
                    "Time for your scheduled sticker spam! (you can stop this with /unsubscribe)",
                )
                await bot.send_sticker(id, sticker_id)
        time.sleep(60 * 60)


def get_token():
    return os.getenv("TOKEN")


if "__main__" == __name__:
    load_dotenv()
    init_pickle()
    thread = Thread(target=asyncio.run, args=(run_regular_spam(),))
    thread.start()

    app = ApplicationBuilder().token(get_token()).build()

    app.add_handler(CommandHandler("sticker", sticker))
    app.add_handler(CommandHandler("add_sticker", start_add_sticker))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("stop_add_sticker", stop_add_sticker))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    app.add_handler(MessageHandler(filters.Sticker.ALL, add_sticker))
    app.add_handler(
        MessageHandler(
            filters.Regex("[hH]elp") | filters.Regex("[hH]ilfe"), there_there
        )
    )

    app.run_polling()
