import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '6451700525:AAHrvFtmXWikJr643nkGYgkDbm8UcFm_9oQ')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '669bb7bcdabb6b9e892a989a6b31a5c7')
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:123@localhost/weatherbot')
    WEBHOOK_URL = 'https://5c6c-212-58-102-223.ngrok-free.app/webhook'
