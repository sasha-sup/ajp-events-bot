import asyncio
import calendar
import random
import re
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, Message, ParseMode,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.types.message import ContentType
from aiogram.utils.markdown import hbold

import config
import db
from config import logger

API_TOKEN = config.TOKEN

# Init bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# nu nado
month_names = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}

# nu krasivo
def get_month_emoji(month_name):
    emojis = {
        "JANUARY": "❄️",
        "FEBRUARY": "❤️",
        "MARCH": "🌼",
        "APRIL": "🌷",
        "MAY": "☀️",
        "JUNE": "🌞",
        "JULY": "🌴",
        "AUGUST": "🌞",
        "SEPTEMBER": "🍂",
        "OCTOBER": "🎃",
        "NOVEMBER": "🍁",
        "DECEMBER": "❄️",
    }
    return emojis.get(month_name, "🗓️")

# https://core.telegram.org/bots/api#markdownv2-style
def escape_special_characters(text):
    special_characters = r'_*[]()~`:/>#+-=|{}.!'
    escaped_text = re.sub(fr'([{re.escape(special_characters)}])', r'\\\1', text)
    return escaped_text

# button
get_btn = types.KeyboardButton("🗓️ Get events")
help_btn = types.KeyboardButton("🆘 Help")

# keyboard
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(get_btn)
markup.add(help_btn)

# /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    try:
        user_id = message.from_user.id
        await db.ensure_user_exists(user_id)
        await message.answer(config.WELCOME_MESSAGE, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup)
        logger.info(f"User {message.from_user.username} started the bot.")
    except Exception as e:
        logger.error(f"Error start: {e}")

# /help
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    try:
        await message.reply(config.HELP_MESSAGE, parse_mode="MarkdownV2", reply_markup=markup)
        logger.info(f"User {message.from_user.username} need help.")
    except Exception as e:
        logger.error(f"Error help: {e}")

# /stop
@dp.message_handler(commands=['stop'])
async def stop_command(message: types.Message):
    try:
        user_id = message.from_user.id
        await db.update_notification_settings(user_id, send_notifications=False)
        logger.info(f"User {message.from_user.username} has opted out of automatic notifications.")
        await message.reply("You have stopped notifications.\n Use the /restart command to restart notifications.")
    except Exception as e:
        logger.error(f"Error stop: {e}")

# /restart
@dp.message_handler(commands=['restart'])
async def stop_command(message: types.Message):
    try:
        user_id = message.from_user.id
        await db.update_notification_settings(user_id, send_notifications=True)
        logger.info(f"User {message.from_user.username} has enabled notifications.")
        await message.reply("You have chosen to get alerted.")
    except Exception as e:
        logger.error(f"Error restart: {e}")

# /poneslas'
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def process_text(message: types.Message):
    try:
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        if not user:
            logger.info(f"User {message.from_user.username} not registered. ")
            await message.answer("You are not registered. Use /start to begin.")
            return
        if message.text == "🗓️ Get events":
            markup = types.InlineKeyboardMarkup()
            available_years = await db.get_available_years()
            row = []
            for year in available_years:
                callback_data = f"inline_button_{year}_pressed"
                year_opt = types.InlineKeyboardButton(year, callback_data=callback_data)
                row.append(year_opt)
                if len(row) == 4:
                    markup.row(*row)
                    row = []
            if row:
                markup.row(*row)
            await message.answer("Select year:", reply_markup=markup)
        elif message.text == "🆘 Help":
            await help_command(message)
    except Exception as e:
        logger.error(f"Error processing text: {e}")



# Inline 1 round
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("inline_button_"))
async def inline_button_callback(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        year_data = callback_query.data.split("_")[2]
        year = int(year_data)
        logger.info(f"User {callback_query.from_user.username} made request")
        markup = types.InlineKeyboardMarkup()
        row = []
        for month_name, month_num in month_names.items():
            emoji = get_month_emoji(month_name) 
            button_text = f"{emoji} {month_name}"
            callback_data = f"choose_month_{year}_{month_num}"
            month_opt = types.InlineKeyboardButton(button_text, callback_data=callback_data)
            row.append(month_opt)
            if len(row) == 3:
                markup.row(*row)
                row = []
        if row:
            markup.row(*row)
        await callback_query.message.answer(f"Select month for {year}:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in inline_button_callback: {e}")

# Inline 2 round
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("choose_month_"))
async def choose_month_callback(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        data_parts = callback_query.data.split("_")
        year = int(data_parts[2])
        month_num = int(data_parts[3])
        month_name = calendar.month_name[month_num]
        events = await db.fetch_events(year, month_num)
        message_text_markdown = ""
        if events:
            message_text_markdown = (f"Events for {year}, {month_name}:\n")
            for event in events:
                try:
                    if 'date' in event and event['date'] and 'place' in event and event['place']:
                        message_text_markdown += f"\n📍 {event['place']}\n🗓️ {event['date']}\n🌐 [{event['event_name']}]({event['event_link']}\n)\n" # Feature: Google Maps API
                    else:
                        message_text_markdown += f"\n📌 {event['event_info']}\n🌐 [{event['event_name']}]({event['event_link']}\n)\n"
                except Exception as e:
                    logger.error(f"Error formatting event: {e}")
            message_text_markdown = escape_special_characters(message_text_markdown)
            await callback_query.message.answer(message_text_markdown, parse_mode="MarkdownV2", disable_web_page_preview=True)
        else:
            await callback_query.message.answer("For the selected month, no events were found.")
    except Exception as e:
        logger.error(f"Error in choose_month_callback: {e}")

# New events sender
async def check_and_send_events():
    try:
        while True:
            users = await db.get_all_user_ids()
            new_events = await db.get_new_events()
            if new_events is None:
                logger.info(f"No new events found.")
            elif len(new_events) == 0:
                logger.info(f"No new events found.")
            else:
                for event in new_events:
                    message_text_markdown = ""
                    try:
                        if 'date' in event and 'place' in event:
                            message_text_markdown = f"📍 {event['place']}\n🗓️ {event['date']}\n🌐 [{event['event_name']}]({event['event_link']})"
                        else:
                            message_text_markdown = f"📌 {event['event_info']}\n🌐 [{event['event_name']}]({event['event_link']})"
                    except Exception as e:
                        logger.error(f"Error formatting event: {e}")
                    message_text_markdown = escape_special_characters(message_text_markdown)
                    try:
                        for user_id in users:
                            await bot.send_message(user_id, message_text_markdown, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            logger.info(f"Sent a message to user {user_id}")
                            await asyncio.sleep(10)
                    except Exception as e:
                        logger.error(f"Error sending messages: {e}")
            interval_in_days = config.REFRESH * 24 * 60 * 60
            await asyncio.sleep(interval_in_days)
    except Exception as e:
        logger.error(f"Error in check_and_send_events: {e}")

async def start_bot():
    await asyncio.gather(
        dp.start_polling(skip_updates=True),
        check_and_send_events())

if __name__ == '__main__':
    asyncio.run(start_bot())
    from aiogram import executor