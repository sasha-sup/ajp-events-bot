import db
from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from config import logger
from keyboards import main as kb
from message_templates import main as msg

from bot import escape_special_characters as md_edit


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
                    message_text_markdown = md_edit(message_text_markdown)
                    try:
                        for user_id in users:
                            await bot.send_message(user_id, message_text_markdown, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            logger.info(f"Sent a message to user {user_id}")
                            await asyncio.sleep(10)
                    except Exception as e:
                        logger.error(f"Error sending messages: {e}")
            interval = 3 * 24 * 60 * 60
            await asyncio.sleep(interval)
    except Exception as e:
        logger.error(f"Error in check_and_send_events: {e}")