from aiogram import Router, F
from aiogram.types import Message

import db
from config import logger
from keyboards import main as kb
from message_templates import main as msg
from handlers.commands import cmd_help

router = Router()

# Help
@router.message(F.text.startswith("🆘 Help"))
async def help(message: Message):
    await cmd_help(message)

# Get events
@router.message(F.text.endswith("Get events"))
async def get_events(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        await message.answer("Select year: ", reply_markup=kb.year())
        await message.delete()
        logger.info(f"User {username} get year.")
    except Exception as e:
        await message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error Get events user_id {user_id}, username {username}: {e}")

# Subscribe for updates
@router.message(F.text.endswith("Subscribe for updates"))
async def check_subscription(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        await message.answer("Subscribe to: ", reply_markup=kb.subscription())
        await message.delete()
        logger.info(f"User {username} wants to subscribe.")
    except Exception as e:
        await message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error Subscribe user_id {user_id}, username {username}: {e}")

# # Register for an event

# @router.message(F.text.endswith("Register for an event"))
# async def check_subscription(message: Message):
#     try:
#         user_id = message.from_user.id
#         username = message.from_user.username
