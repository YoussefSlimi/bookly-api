from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from src.db.models import Book
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


engine = create_async_engine(
    Config.DATABASE_URL
)

async def init_db():
    async with engine.begin() as conn :
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() :
    Session = sessionmaker(
        engine,
        class_= AsyncSession,
        expire_on_commit= False
    )
    async with Session() as session :
        yield session
