from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy import select
from database import AsyncSessionLocal, User
from keyboards.inline import start_keyboard, back_to_start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            session.add(User(user_id=user_id, username=username, first_name=first_name))
            await session.commit()

    await message.answer(
        f"Assalomu alaykum, {first_name}! 🎬\n"
        "Men kino botiman. Kinolarni raqam yoki nom bo'yicha qidirishingiz mumkin.\n"
        "Quyidagi tugmalardan foydalaning:",
        reply_markup=start_keyboard()
    )

@router.callback_query(F.data == "start_menu")
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Assalomu alaykum, {callback.from_user.first_name}! 🎬\n"
        "Men kino botiman. Kinolarni raqam yoki nom bo'yicha qidirishingiz mumkin.\n"
        "Quyidagi tugmalardan foydalaning:",
        reply_markup=start_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Bot haqida</b>\n\n"
        "Bu bot orqali siz kinolarni raqam yoki nom bo'yicha qidirishingiz, "
        "ularning tafsilotlarini ko'rishingiz va tomosha qilishingiz mumkin.\n\n"
        "Yangi kinolarni faqat admin qo'sha oladi.\n"
        "Bot yaratuvchisi: @YourUsername"
    )
    await callback.message.edit_text(text, reply_markup=back_to_start_keyboard())
    await callback.answer()