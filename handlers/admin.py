from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from database import AsyncSessionLocal, User, Movie
from config import ADMIN_IDS, CHANNEL_ID
from utils import get_channel_link, logger
import asyncio

router = Router()

class MovieUpload(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()

# Admin tekshirish filtri
async def admin_filter(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

@router.message(F.video | F.document, admin_filter)
async def admin_video_received(message: Message, state: FSMContext):
    """Admin video yuborganida."""
    if message.video:
        file_id = message.video.file_id
    elif message.document and message.document.mime_type.startswith("video/"):
        file_id = message.document.file_id
    else:
        await message.answer("Iltimos, faqat video fayl yuboring (mp4, mkv).")
        return

    await state.update_data(file_id=file_id, video_message_id=message.message_id)
    await state.set_state(MovieUpload.waiting_for_title)
    await message.answer("Kino nomini yuboring:")

@router.message(MovieUpload.waiting_for_title, admin_filter)
async def process_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) > 200:
        await message.answer("Nom juda uzun. 200 belgidan oshmasin. Qaytadan yuboring.")
        return
    await state.update_data(title=title)
    await state.set_state(MovieUpload.waiting_for_description)
    await message.answer("Kino tavsifini yuboring (yoki /skip bosing):")

@router.message(MovieUpload.waiting_for_description, admin_filter)
async def process_description(message: Message, state: FSMContext):
    if message.text == "/skip":
        description = ""
    else:
        description = message.text.strip()

    data = await state.get_data()
    file_id = data["file_id"]
    title = data["title"]
    video_msg_id = data["video_message_id"]

    async with AsyncSessionLocal() as session:
        # Keyingi tartib raqamni olish
        result = await session.execute(select(func.max(Movie.movie_number)))
        max_num = result.scalar() or 0
        next_number = max_num + 1

        # Videoni asosiy kanalga forward qilish
        try:
            forwarded = await message.bot.forward_message(
                chat_id=CHANNEL_ID,
                from_chat_id=message.chat.id,
                message_id=video_msg_id
            )
            channel_msg_id = forwarded.message_id
        except Exception as e:
            logger.error(f"Forward qilishda xato: {e}")
            await message.answer("Kino kanalga yuborilmadi. Xatolik yuz berdi.")
            await state.clear()
            return

        # Ma'lumotlar bazasiga saqlash
        movie = Movie(
            movie_number=next_number,
            title=title,
            description=description,
            file_id=file_id,
            channel_message_id=channel_msg_id,
            channel_chat_id=CHANNEL_ID,
            added_by=message.from_user.id
        )
        session.add(movie)
        await session.commit()

        link = get_channel_link(CHANNEL_ID, channel_msg_id)
        await message.answer(
            f"✅ Kino #{next_number} muvaffaqiyatli qo'shildi!\n"
            f"📎 Havola: {link}",
            disable_web_page_preview=True
        )
    await state.clear()

@router.message(Command("stats"), admin_filter)
async def cmd_stats(message: Message):
    async with AsyncSessionLocal() as session:
        movie_count = await session.scalar(select(func.count()).select_from(Movie))
        user_count = await session.scalar(select(func.count()).select_from(User))
    await message.answer(f"📊 Statistika:\n\n🎬 Kinolar soni: {movie_count}\n👥 Foydalanuvchilar soni: {user_count}")

@router.message(Command("users"), admin_filter)
async def cmd_users(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.user_id, User.first_name).limit(50))
        users = result.all()
        if not users:
            await message.answer("Hali foydalanuvchilar yo'q.")
            return
        text = "👥 Foydalanuvchilar (birinchi 50 ta):\n\n"
        for u in users:
            text += f"• {u.user_id} - {u.first_name or 'Ism yo‘q'}\n"
        await message.answer(text)

@router.message(Command("broadcast"), admin_filter)
async def cmd_broadcast(message: Message):
    if not message.reply_to_message:
        await message.answer("Iltimos, xabarni reply qilib /broadcast buyrug'ini yuboring.")
        return
    text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        await message.answer("Matnli xabarni reply qiling.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.user_id))
        user_ids = [row[0] for row in result.all()]

    success = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Xabar yuborilmadi {uid}: {e}")
    await message.answer(f"✅ Xabar {success}/{len(user_ids)} foydalanuvchiga yuborildi.")