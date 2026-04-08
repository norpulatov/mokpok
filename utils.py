import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_channel_link(chat_id: str, message_id: int) -> str:
    """Telegram kanal posti havolasini yaratish."""
    if chat_id.startswith("-100"):
        clean_id = chat_id[4:]
    else:
        clean_id = chat_id
    return f"https://t.me/c/{clean_id}/{message_id}"

def build_movies_keyboard(movies, page: int, total_pages: int):
    """Kinolar ro'yxati uchun inline tugmalar."""
    builder = InlineKeyboardBuilder()
    for movie in movies:
        builder.button(
            text=f"#{movie.movie_number} - {movie.title[:30]}",
            callback_data=f"view_{movie.movie_number}"
        )
    builder.adjust(1)
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        builder.row(*nav_buttons)
    return builder.as_markup()