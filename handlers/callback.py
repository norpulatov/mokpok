from aiogram import Router, F
from aiogram.types import CallbackQuery
from .movies import show_movies_page, show_movie_details
from keyboards.inline import start_keyboard

router = Router()

@router.callback_query(F.data == "movies_list")
async def movies_list_callback(callback: CallbackQuery):
    await show_movies_page(callback, page=1, edit=True)
    await callback.answer()

@router.callback_query(F.data == "search_prompt")
async def search_prompt_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "Qidirish uchun kino raqami yoki nomini yuboring:",
        reply_markup=None
    )
    # Wait for user message; we can set state or just reply; here we'll use a simple approach
    # We'll instruct user to use /search command
    await callback.message.answer("Iltimos, /search buyrug'idan foydalaning. Masalan: /search 42")
    await callback.answer()