from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, func, or_
from database import AsyncSessionLocal, Movie
from utils import build_movies_keyboard, get_channel_link
from keyboards.inline import movie_detail_keyboard, back_to_start_keyboard
import math

router = Router()

async def show_movies_page(target, page: int = 1, edit: bool = True):
    per_page = 10
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Movie).order_by(Movie.movie_number).offset((page-1)*per_page).limit(per_page)
        )
        movies = result.scalars().all()
        total = await session.scalar(select(func.count()).select_from(Movie))
        total_pages = math.ceil(total / per_page) if total else 1

    if not movies:
        text = "Hali hech qanday kino qo'shilmagan."
        if edit:
            if isinstance(target, CallbackQuery):
                await target.message.edit_text(text, reply_markup=back_to_start_keyboard())
            else:
                await target.edit_text(text, reply_markup=back_to_start_keyboard())
        else:
            await target.answer(text, reply_markup=back_to_start_keyboard())
        return

    text = f"🎬 <b>Kinolar ro'yxati</b> (sahifa {page}/{total_pages}):\n\n"
    for m in movies:
        text += f"#{m.movie_number} - {m.title}\n"

    keyboard = build_movies_keyboard(movies, page, total_pages)
    if edit:
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, reply_markup=keyboard)
        else:
            await target.edit_text(text, reply_markup=keyboard)
    else:
        await target.answer(text, reply_markup=keyboard)

@router.message(Command("movies"))
async def cmd_movies(message: Message):
    await show_movies_page(message, page=1, edit=False)

@router.callback_query(F.data.startswith("page_"))
async def pagination_callback(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    await show_movies_page(callback, page=page, edit=True)
    await callback.answer()

@router.message(Command("movie"))
async def cmd_movie(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Iltimos, kino raqamini kiriting: /movie 123")
        return
    try:
        num = int(args[1])
    except ValueError:
        await message.answer("Kino raqami son bo'lishi kerak.")
        return
    await show_movie_details(message, num)

async def show_movie_details(target, movie_number: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Movie).where(Movie.movie_number == movie_number))
        movie = result.scalar_one_or_none()
        if not movie:
            text = f"❌ #{movie_number} raqamli kino topilmadi."
            if isinstance(target, Message):
                await target.answer(text)
            else:
                await target.message.edit_text(text, reply_markup=back_to_start_keyboard())
            return
        # Ko'rishlar sonini oshirish
        movie.views_count += 1
        await session.commit()
        watch_url = get_channel_link(movie.channel_chat_id, movie.channel_message_id)
        text = (
            f"🎬 <b>#{movie.movie_number} - {movie.title}</b>\n\n"
            f"📝 {movie.description or 'Tavsif mavjud emas'}\n\n"
            f"👁 Ko'rishlar: {movie.views_count}\n"
            f"📅 Qo'shilgan: {movie.added_at.strftime('%Y-%m-%d')}"
        )
        keyboard = movie_detail_keyboard(movie_number, watch_url)
        if isinstance(target, Message):
            await target.answer(text, reply_markup=keyboard, disable_web_page_preview=True)
        else:
            await target.message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)

@router.callback_query(F.data.startswith("view_"))
async def view_callback(callback: CallbackQuery):
    movie_number = int(callback.data.split("_")[1])
    await show_movie_details(callback, movie_number)
    await callback.answer()

@router.callback_query(F.data.startswith("refresh_"))
async def refresh_callback(callback: CallbackQuery):
    movie_number = int(callback.data.split("_")[1])
    await show_movie_details(callback, movie_number)
    await callback.answer()

@router.message(Command("search"))
async def cmd_search(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        await message.answer("Qidirish uchun kino raqami yoki nomini kiriting:\nMasalan: /search 42 yoki /search Avatar")
        return
    query = args[1].strip()
    async with AsyncSessionLocal() as session:
        # Avval raqam bo'yicha tekshirish
        if query.isdigit():
            result = await session.execute(select(Movie).where(Movie.movie_number == int(query)))
            movie = result.scalar_one_or_none()
            if movie:
                await show_movie_details(message, movie.movie_number)
                return
        # Nom bo'yicha qidirish
        result = await session.execute(
            select(Movie).where(Movie.title.ilike(f"%{query}%")).order_by(Movie.movie_number).limit(20)
        )
        movies = result.scalars().all()
        if not movies:
            await message.answer(f"❌ '{query}' bo'yicha hech narsa topilmadi.")
            return
        if len(movies) == 1:
            await show_movie_details(message, movies[0].movie_number)
            return
        text = f"🔍 '{query}' bo'yicha topilgan kinolar:\n\n"
        for m in movies:
            text += f"#{m.movie_number} - {m.title}\n"
        text += "\nKino raqamini tanlang yoki /movie raqam buyrug'ini yuboring."
        await message.answer(text)