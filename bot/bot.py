import asyncio
import os
import re

from aiogram import Bot, Dispatcher

import config
import db
from config import logger
from handlers import commands, buttons
from callbacks import callbacks

async def log_dir():
    try:
        dir_path = "/app/log"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")
        else:
            logger.info(f"Directory already exists: {dir_path}")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        raise e

# https://core.telegram.org/bots/api#markdownv2-style
def escape_special_characters(text):
    special_characters = r'_*~`:/>#+-=|{}.!'
    escaped_text = re.sub(fr'([{re.escape(special_characters)}])', r'\\\1', text)
    return escaped_text

async def main():
    await log_dir()
    await db.create_tables_if_exists()
    bot = Bot(config.TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        commands.router,
        buttons.router,
        callbacks.router
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
