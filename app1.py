from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import requests
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from telegram import Message, Bot
from config import Config
from models import Log, init_models, Base
from weather_api import get_weather
import asyncio
from models import add_log, get_logs_from_db, get_user_settings
from typing import Optional

DATABASE_URL = Config.DATABASE_URL

app = FastAPI(
    title="Weather Telegram Bot API",
    description="API для взаимодействия с Telegram-ботом и получения логов",
    version="1.0.0"
)

# Создаем асинхронный движок и сессию
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
TOKEN = Config.TELEGRAM_BOT_TOKEN
bot = Bot(token=TOKEN)

async def get_db():
    async with async_session() as session:
        yield session


async def start(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    print("Bot step start:", bot)
    await bot.send_message(chat_id=chat_id, text='Привет! Я бот для получения информации о погоде.')
    try:
            await add_log(str(user_id), '/start', str(response))
    except Exception as e:
        print("Error during commit:", e)


async def weather(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    command_parts = message.text.split(maxsplit=1)
    print('command_parts:', command_parts)
    
    if len(command_parts) < 2:
        settings = await get_user_settings(user_id)
        if settings:
            city = settings.city
        else:
            await bot.send_message(chat_id=chat_id, text='Пожалуйста, укажите город после команды /weather.')
            return
    
    city = command_parts[1]
    print('city:', city)
    weather_info = await get_weather(city)
    
    if weather_info:
        response = (
            f"Температура: {weather_info['temperature']}°C\n"
            f"Ощущается как: {weather_info['feels_like']}°C\n"
            f"Описание: {weather_info['description']}\n"
            f"Влажность: {weather_info['humidity']}%\n"
            f"Скорость ветра: {weather_info['wind_speed']} м/с"
        )
        try:
            await add_log(str(user_id), '/weather', str(response))
        except Exception as e:
            print("Error during commit:", e)
            # await db.rollback()
        
        # await db.commit()
        print("Bot step weather:", bot)
        await bot.send_message(chat_id=chat_id, text=response)
        
    else:
        await bot.send_message(chat_id=chat_id, text='Город не найден. Проверьте правильность написания.')

@app.get('/logs')
async def get_logs_route(skip: int = 0, limit: int = 10, user_id: int = None):
    try:
        logs = await get_logs_from_db(user_id)
        logs_dict = [{
            'user_id': log.user_id,
            'command': log.command,
            'request_time': log.request_time.isoformat() if isinstance(log.request_time, datetime) else log.request_time,
            'response': log.response
        } for log in logs[skip:skip+limit]]
        return JSONResponse(content=logs_dict)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/logs/{user_id:str}')
async def get_user_logs_route(user_id: str, skip: int = 0, limit: int = 10, start_time: Optional[str] = None, end_time: Optional[str] = None):
    try:
        logs = await get_logs_from_db(user_id)

        #фильтрация по времени запроса

        if start_time:
            start_time = datetime.fromisoformat(start_time)
            logs = [log for log in logs if log.request_time >= start_time]


        logs_dict = [{
            'user_id': log.user_id,
            'command': log.command,
            'request_time': log.request_time.isoformat() if isinstance(log.request_time, datetime) else log.request_time,
            'response': log.response
        } for log in logs[skip:skip+limit]]
        return JSONResponse(content=logs_dict)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/webhook')
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        update_data = await request.json()
        if 'message' in update_data:
            message_data = update_data['message']
            message = Message.de_json(message_data, bot)
            if message.text.startswith('/start'):
                await start(message)
            elif message.text.startswith('/weather'):
                await weather(message)
    except Exception as e:
        print("Exception:", e)
    return 'ok'

# async def set_webhook():
#     webhook_url = Config.WEBHOOK_URL
#     await bot.set_webhook(url=webhook_url)
#     print('Webhook successfully set')

# @app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    TOKEN = Config.TELEGRAM_BOT_TOKEN
    webhook_url = Config.WEBHOOK_URL

    asyncio.run(on_startup())

    url = f'https://api.telegram.org/bot{TOKEN}/setWebhook'
    payload = {
        'url': webhook_url,
        'allowed_updates': ["message", "callback_query", "pre_checkout_query", "successful_payment"]
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Webhook set successfully")
    else:
        print(f"Failed to set webhook: {response.text}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)