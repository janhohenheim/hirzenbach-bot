#!/usr/bin/env python3

import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from threading import Thread
import gpt3
from env import Env
from persistance import Data
import commands


def main():
    Data.init()
    gpt3.setup_openai()
    thread = Thread(target=asyncio.run, args=(commands.run_regular_spam(),))
    thread.start()

    app = ApplicationBuilder().token(Env.read().telegram_token).build()

    app.add_handler(CommandHandler("sticker", commands.sticker))
    app.add_handler(CommandHandler("add_sticker", commands.start_add_sticker))
    app.add_handler(CommandHandler("help", commands.help))
    app.add_handler(CommandHandler("stop_add_sticker", commands.stop_add_sticker))
    app.add_handler(CommandHandler("subscribe", commands.subscribe))
    app.add_handler(CommandHandler("unsubscribe", commands.unsubscribe))
    app.add_handler(CommandHandler("inspire", commands.inspire))

    app.add_handler(MessageHandler(filters.Sticker.ALL, commands.add_sticker))
    app.add_handler(
        MessageHandler(
            filters.Regex("[hH]elp") | filters.Regex("[hH]ilfe"), commands.there_there
        )
    )
    app.add_handler(MessageHandler(filters.Regex(r"\?"), commands.answer_question))
    app.run_polling()


if "__main__" == __name__:
    main()
