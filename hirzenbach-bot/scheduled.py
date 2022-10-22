from telegram.ext import CallbackContext
from persistence import get_sticker_subscribers, get_morning_subscribers, get_stickers
import random
from datetime import datetime
from gpt3 import complete_prompt
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo('CET')


async def send_sticker_spam(context: CallbackContext):
    if _is_day():
        stickers = get_stickers()
        for id in get_sticker_subscribers():
            sticker_id = random.choice(stickers)
            await context.bot.send_sticker(id, sticker_id)


async def send_morning_spam(context: CallbackContext):
    greeting = complete_prompt(
        """The following messages were rated UK's most heartwarming and inspiring "good morning" greetings people received from friends.
- Good morning, sunshine! I hope you have a great day.
- Sun is rising and so are you. Good morning!
- Hi! The world is waking up and cannot wait to see you shine today.
- Morning, sleepyhead :) Take some time today to do at least one thing you love.
- Good morning! Try to smile today. It makes you look beautiful!
-"""
    )
    for id in get_morning_subscribers():
        await context.bot.send_message(id, greeting)


def _is_day() -> bool:
    now = _get_time()
    return 9 < now.hour < 21


def _get_time() -> datetime:
    # don't care about summer time
    # also, this is a purely European bot, deal with it 😎
    return datetime.now(TIMEZONE)

