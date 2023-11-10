from aiogram.filters.callback_data import CallbackData
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, KeyboardButtonPollType,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def subscription():
    builder = InlineKeyboardBuilder()
    options = ["", "", "", ""] # OPTION HERE~ BELT DIVISON GENDER ETC
    for option in options:
        builder.row(InlineKeyboardButton(text=option, callback_data="228")),
        builder.adjust(4)
    return builder.as_markup()

def year():
    builder = InlineKeyboardBuilder()
    years = [str(year) for year in range(2023, 2025)]
    for year in years:
        builder.row(InlineKeyboardButton(text=year, callback_data=f"year_{year}")),
        builder.adjust(2)
    return builder.as_markup()

def month():
    builder = InlineKeyboardBuilder()
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for i, month in enumerate(months, start=1):
        builder.row(InlineKeyboardButton(text=month, callback_data=f"month_{i}")),
        builder.adjust(3)
    return builder.as_markup()

def main():
    kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗓️ Get events")
        ],
        [
            KeyboardButton(text="🔔 Subscribe for updates")
        ],
        [
            KeyboardButton(text="🆘 Help")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Select action: "
    )
    return kb