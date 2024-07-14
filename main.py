import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import TOKEN


# API для получения прогноза погоды
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
WEATHER_API_KEY = '2029b8b51e4bae5500421b9230bd0bf5'  # OpenWeatherMap API key from 14/07/2024
CITY = 'Moscow'

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Я ваш бот для прогноза погоды. Используйте /weather для получения прогноза.")

# Команда /help
@dp.message(Command("help"))
async def send_help(message: Message):
    await message.answer("Вы можете использовать команду /weather для получения прогноза погоды.")

# Команда /weather
@dp.message(Command("weather"))
async def send_weather(message: Message):
    url = f'{WEATHER_API_URL}?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()

        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        weather_info = f'Погода в {CITY}:\nТемпература: {temperature}°C\nОписание: {weather_description}'
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        weather_info = 'Ошибка HTTP. Проверьте правильность URL и параметров запроса.'
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        weather_info = 'Не удалось получить данные о погоде.'
    except Exception as e:
        logger.error(f"Error: {e}")
        weather_info = 'Произошла ошибка при обработке данных о погоде.'

    await message.answer(weather_info)

# Обработка ошибок через middleware
class ErrorHandlerMiddleware:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            self.logger.exception(f"Update: {event} caused error: {e}")
            if isinstance(event, Message):
                await event.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
            return True

async def main():
    # Добавляем middleware для обработки ошибок
    dp.message.middleware(ErrorHandlerMiddleware())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())