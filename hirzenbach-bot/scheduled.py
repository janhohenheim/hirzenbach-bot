from env import Env
import time
import telegram
from persistance import Data
import random
from datetime import timezone, datetime, timedelta
from gpt3 import complete_prompt


async def run_regular_spam():
    while True:
        time.sleep(60 * 60)
        if not is_day():
            continue
        data = Data.read()
        bot = build_telegram_bot()
        async with bot:
            for id in data.sticker_subscribers:
                data = Data.read()
                sticker_id = random.choice(list(data.sticker_pool))
                await bot.send_sticker(id, sticker_id)


async def run_morning_spam():
    while True:
        time.sleep(60 * 60)
        if not is_morning():
            continue
        data = Data.read()
        bot = build_telegram_bot()
        greeting = complete_prompt(
            """The following messages were rated UK's most heartwarming and inspiring "good morning" greetings people received from friends.
- Good morning, sunshine! I hope you have a great day.
- Sun is rising and so are you. Good morning!
- Hi! The world is waking up and cannot wait to see you shine today.
- Morning, sleepyhead :) Take some time today to do at least one thing you love.
- Good morning! Try to smile today. It makes you look beautiful!
-"""
        )
        async with bot:
            for id in data.morning_subscribers:
                await bot.send_message(id, greeting)


def build_telegram_bot() -> telegram.Bot:
    token = Env.read().telegram_token
    return telegram.Bot(token)


def get_time() -> datetime:
    # don't care about summer time
    # also, this is a purely European bot, deal with it 😎
    cet = timezone(timedelta(hours=1))
    return datetime.now(cet)


def is_day() -> bool:
    now = get_time()
    return 9 < now.hour < 21


def is_morning() -> bool:
    now = get_time()
    return now.hour == 7
