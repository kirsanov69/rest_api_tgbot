import httpx
from config import Config

async def get_weather(city):
    params = {
        'q': city,
        'appid': Config.WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(Config.WEATHER_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
        print("Weather info:", weather_info)
        return weather_info
    else:
        print("Error during request:", response.text)
        return None