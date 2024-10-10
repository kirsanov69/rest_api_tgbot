import asyncio
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from config import Config

DATABASE_URL = Config.DATABASE_URL
Base = declarative_base()

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    command = Column(String(100), nullable=False)
    request_time = Column(DateTime, default=datetime.now)
    response = Column(String(500), nullable=False)

engine = create_async_engine(DATABASE_URL)
base = declarative_base()
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class UserSettings(Base):
    __tablename__ = 'user_settings'
    user_id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Dependency
async def get_session():
    async with async_session() as session:
        yield session

async def add_log(user_id: str, command: str, response: str):
    try:
        async with async_session() as session:
            log = Log(user_id=user_id, command=command, response=response)
            session.add(log)
            print("Log entry added successfully")
            await session.commit()
            print("Log entry committed successfully")
    except Exception as e:
        print("Error during commit:", e)
        await session.rollback()


async def get_logs_from_db(user_id: str):
    try:
        async with async_session() as session:
            if user_id:
                query = select(Log).filter_by(user_id=user_id)
            else:
                query = select(Log)
            
            result = await session.execute(query)
            logs = result.scalars().all()
            print(logs)
            return logs
    except Exception as e:
        print(e)


async def get_user_settings(user_id: int):
    try:
        async with async_session() as session:
            query = select(UserSettings).filter_by(user_id=user_id)
            result = await session.execute(query)
            settings = result.scalars().first()
            return settings
    except Exception as e:
        print(e)


async def set_user_settings(user_id: int, city: str):
    settings = await get_user_settings(user_id)
    if settings:
        if settings.city != city:
            try:
                async with async_session() as session:
                    query = select(UserSettings).filter_by(user_id=user_id)
                    result = await session.execute(query)
                    settings = result.scalars().first()
                    settings.city = city
                    await session.commit()
            except Exception as e:
                print(e)
# if __name__ == '__main__':
#     asyncio.run(get_logs_from_db('597847427'))