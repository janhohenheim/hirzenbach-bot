#!/usr/bin/env python3

import asyncio
from typing import Callable
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    JobQueue,
)
from threading import Thread
import gpt3
from env import Env
from persistence import init_database
from datetime import timedelta, time
import commands
import scheduled


def _get_spam_thread(callback: Callable) -> Thread:
    return Thread(target=asyncio.run, args=(callback(),))


def main():
    init_database()
    gpt3.setup_openai()

    job_queue = JobQueue()
    job_queue.scheduler.timezone = scheduled.TIMEZONE
    app = ApplicationBuilder().job_queue(job_queue).token(Env.read().telegram_token).build()

    job_queue.run_repeating(scheduled.send_sticker_spam, interval=timedelta(hours=1))
    job_queue.run_daily(scheduled.send_morning_spam, time=time(7, 0))

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
    app.add_handler(CommandHandler("forget", commands.forget))

    app.add_handler(MessageHandler(filters.Sticker.ALL, commands.add_sticker))
    app.add_handler(
        MessageHandler(
            filters.Regex("[hH]elp") | filters.Regex("[hH]ilfe"), commands.there_there
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Regex('^\\s*(-?\\d+)\\s*/\\s*(-?\\d+)\\s*$'), commands.fraction
        )
    )
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), commands.generic_message)
    )
    app.run_polling()


if "__main__" == __name__:
    main()
