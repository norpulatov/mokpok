from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime
from config import DATABASE_URL

# PostgreSQL uchun async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    movie_number = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_id = Column(String, nullable=True)  # video file_id
    channel_message_id = Column(BigInteger, nullable=False)  # asosiy kanaldagi xabar ID
    channel_chat_id = Column(String, nullable=False)  # asosiy kanal ID
    added_by = Column(BigInteger, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    views_count = Column(Integer, default=0)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)