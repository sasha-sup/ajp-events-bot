import db
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from config import logger
from keyboards import main as kb
from message_templates import main as msg

router = Router()

# /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        await db.ensure_user_exists(user_id, username)
        await message.answer(msg.WELCOME_MESSAGE, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=kb.main())
        logger.info(f"User {username} started the bot.")
    except Exception as e:
        await message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error start user_id {user_id}, username {username}: {e}")

# /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        user = await db.get_user(user_id)
        if user: 
            await message.answer(msg.WELCOME_MESSAGE, parse_mode="MarkdownV2", reply_markup=kb.main())
            await message.delete()
            logger.info(f"User {username} need help.")
        else:
            await message.answer("You are not registered. Use /start to begin.")
    except Exception as e:
        await message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error help user_id {user_id}, username {username}: {e}")

# /stop
@router.message(Command("stop"))
async def cmd_stop(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        user = await db.get_user(user_id)
        if user: 
            await message.answer(msg.STOP_MESSAGE, reply_markup=kb.main())
            # ФУНКЦИЯ ОТПИСКИ ОТ ВСЕГО ИЛИ ОТКЛЮЧЕНИЕ НОТИФИКАЦИЙ
            logger.info(f"User {username} stop subscription.")
        else:
            await message.answer("You are not registered. Use /start to begin.")
    except Exception as e:
        await message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error stop user_id {user_id}, username {username}: {e}")

# /restart 
# .....

