#!/usr/bin/env python3

import asyncio
from sched import scheduler
from typing import Callable
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from threading import Thread
import gpt3
from env import Env
from persistance import Data, init_database, migrate_stickers_to_sqlite
import commands
import scheduled


def _get_spam_thread(callback: Callable) -> Thread:
    return Thread(target=asyncio.run, args=(callback(),))


def main():
    Data.init()
    init_database()
    migrate_stickers_to_sqlite()
    gpt3.setup_openai()
    threads = [
        _get_spam_thread(callback)
        for callback in [scheduled.run_morning_spam, scheduled.run_regular_spam]
    ]
    for thread in threads:
        thread.start()

    app = ApplicationBuilder().token(Env.read().telegram_token).build()

    app.add_handler(CommandHandler("sticker", commands.sticker))
    app.add_handler(CommandHandler("add_sticker", commands.start_add_sticker))
    app.add_handler(CommandHandler("help", commands.help))
    app.add_handler(CommandHandler("stop_add_sticker", commands.stop_add_sticker))
    app.add_handler(CommandHandler("subscribe_sticker", commands.subscribe_sticker))
    app.add_handler(CommandHandler("subscribe_morning", commands.subscribe_morning))
    app.add_handler(CommandHandler("unsubscribe_sticker", commands.unsubscribe_sticker))
    app.add_handler(CommandHandler("unsubscribe_morning", commands.unsubscribe_morning))
    app.add_handler(CommandHandler("inspire", commands.inspire))
    app.add_handler(CommandHandler("code", commands.code))

    app.add_handler(MessageHandler(filters.Sticker.ALL, commands.add_sticker))
    app.add_handler(
        MessageHandler(
            filters.Regex("[hH]elp") | filters.Regex("[hH]ilfe"), commands.there_there
        )
    )
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), commands.generic_message)
    )
    app.run_polling()


if "__main__" == __name__:
    main()
