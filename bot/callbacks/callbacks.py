from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswer
from bot import escape_special_characters as md_edit
from config import logger
from db import fetch_events
from keyboards import main as kb
from message_templates import main as msg

router = Router()

@router.callback_query(F.data.startswith("year_"))
async def year_callback(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username
        global year
        year = callback.data.split("_")[1]
        logger.info(f"User {user_id}, {username} made year request")
        await callback.message.answer(f"Select month for {year}:", reply_markup=kb.month())
        await callback.message.delete()
    except Exception as e:
        await callback.message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error in year_callback user_id {user_id}, username {username}: {e}")

@router.callback_query(F.data.startswith("month_"))
async def month_callback(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username
        logger.info(f"User {user_id}, {username} made month request")
        month = int(callback.data.split("_")[1])
        events = await fetch_events(int(year), int(month))
        message_text_markdown = ""
        if events:
            message_text_markdown = (f"Events for {year}, {month}:\n")
            for event in events:
                try:
                    if 'date' in event and event['date'] and 'place' in event and event['place']:
                        message_text_markdown += f"\n📍 {event['place']}\n🗓️ {event['date']}\n🌐 [{event['event_name']}]({event['event_link']}\n)\n"
                    else:
                        message_text_markdown += f"\n📌 {event['event_info']}\n🌐 [{event['event_name']}]({event['event_link']}\n)\n"
                except Exception as e:
                    logger.error(f"Error formatting event: {e}")
            message_text_markdown = md_edit(message_text_markdown)
            await callback.message.answer(message_text_markdown, parse_mode="MarkdownV2", disable_web_page_preview=True)
            await callback.message.delete()
        else:
            await callback.message.answer("For the selected month, no events were found.")
            await callback.message.delete()
    except Exception as e:
        await callback.message.answer(msg.ERROR_MESSAGE)
        logger.error(f"Error in month_callback user_id {user_id}, username {username}: {e}")