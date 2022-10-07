from env import Env
import time
import telegram
from persistance import Data
import random


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
