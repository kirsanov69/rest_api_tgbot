# Weather Telegram Bot

This is a Telegram bot that provides weather information using the OpenWeatherMap API. The bot is built with FastAPI and uses PostgreSQL for storing user logs and settings.

## Features

- Get current weather information for a specified city.
- Store user settings, such as the preferred city for weather requests.
- Log user commands and responses.

## Requirements

- Docker
- Docker Compose
- Telegram Bot Token
- OpenWeatherMap API Key

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/kirsanov69/rest_api_tgbot
    cd weather-telegram-bot
    ```

2. Create a `.env` file in the root directory and add your environment variables:

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    WEATHER_API_KEY=your_openweathermap_api_key
    DATABASE_URL=postgresql+asyncpg://postgres:123@db/weatherbot
    WEBHOOK_URL=your_webhook_url
    ```

3. Build and run the Docker containers:

    ```sh
    docker-compose up --build
    ```

4. Access the API documentation at [http://localhost:5000/docs](http://localhost:5000/docs).

## Usage

- Start a conversation with the bot on Telegram by sending the `/start` command.
- Get weather information by sending the `/weather <city>` command.
- The bot will remember your preferred city for future weather requests.

## Contributing

Feel free to submit issues and pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
