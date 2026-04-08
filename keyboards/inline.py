from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Kinolar ro'yxati", callback_data="movies_list")
    builder.button(text="🔍 Qidirish", callback_data="search_prompt")
    builder.button(text="ℹ️ Bot haqida", callback_data="about")
    builder.adjust(1)
    return builder.as_markup()

def movie_detail_keyboard(movie_number: int, watch_url: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Ko'rish", url=watch_url)
    builder.button(text="🔄 Yangilash", callback_data=f"refresh_{movie_number}")
    builder.button(text="🏠 Bosh menyu", callback_data="start_menu")
    builder.adjust(1)
    return builder.as_markup()

def back_to_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Bosh menyu", callback_data="start_menu")
    return builder.as_markup()