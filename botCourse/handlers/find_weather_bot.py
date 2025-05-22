from aiogram import Bot, Router, types, F
from aiogram.filters.command import Command
from aiogram.types import Message
import matplotlib.pyplot as plt
import asyncio
import requests
import logging
from io import BytesIO
from datetime import datetime, timedelta

from config import TOKEN

bot = Bot(TOKEN)
router = Router()

def generate_weather_chart(forecast_data):
    dates = []
    temps = []
    
    for day in forecast_data['list']:
        # Беремо прогноз на 12:00 кожного дня (щоб уникнути занадто багато точок)
        if day['dt_txt'].endswith('12:00:00'):
            dates.append(day['dt_txt'][:10])
            temps.append(day['main']['temp'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, temps, marker='o', linestyle='-', color='tab:blue')
    plt.title('Прогноз погоди на 5 днів')
    plt.xlabel('Дата')
    plt.ylabel('Температура (°C)')
    plt.grid(True)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

@router.message(F.text == "Погода у вашому місті")
async def start_command(message: Message):
    await message.answer('Привіт! Напишіть назву міста, щоб дізнатися погоду.')

@router.message(F.text)
async def get_weather(message: Message):
    city = message.text.strip()
    try:
        # Отримуємо поточну погоду
        current_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        current_data = requests.get(current_url).json()

        # Отримуємо прогноз на 5 днів
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        forecast_data = requests.get(forecast_url).json()

        # Поточна погода
        current_temp = current_data['main']['temp']
        feels_like = current_data['main']['feels_like']
        wind = current_data['wind']['speed']
        humidity = current_data['main']['humidity']
        description = current_data['weather'][0]['description']

        # Формуємо текст повідомлення
        text_response = (
            f"Поточна погода в місті {city}:\n"
            f"🌡 Температура: {current_temp}°C\n"
            f"🤔 Відчувається як: {feels_like}°C\n"
            f"🌬 Вітер: {wind} м/с\n"
            f"💧 Вологість: {humidity}%\n"
            f"☁️ Опис: {description}\n\n"
            f"Прогноз на 5 днів:"
        )

        # Генеруємо графік
        chart_buffer = generate_weather_chart(forecast_data)
        
        # Відправляємо повідомлення
        await message.answer_photo(
            photo=types.BufferedInputFile(
                file=chart_buffer.getvalue(),
                filename='weather_forecast.png'
            ),
            caption=text_response
        )
        
    except KeyError:
        await message.answer(f"❌ Не вдалося знайти місто: {city}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())