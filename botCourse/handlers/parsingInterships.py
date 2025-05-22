import requests
import logging
from bs4 import BeautifulSoup
from aiogram import Bot, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import asyncio

from config import TOKEN

bot = Bot(token=TOKEN)
router = Router()

parsed_jobs = []
# Функція для парсингу вакансій
url = 'https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp&employment=remote'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

jobs = soup.find_all('li', class_ = 'mb-4')[:7]
length = int(len(jobs))


for job in jobs:
                title = job.find('a', class_ = 'job-item__title-link').text.strip()
                job_link = job.find('a', class_ = 'job-item__title-link').get('href')
                link = f'https://djinni.co{job_link}'

                watched = job.find_all('span', class_ = 'text-nowrap')[0].text.strip()
                feedback = job.find_all('span', class_ = 'text-nowrap')[1].text.strip()
                info = f'{watched} {feedback}'
                data = job.find_all('span', class_ = 'text-nowrap')[2].text.strip()


                worked_for = job.find('div', class_ = 'fw-medium d-flex flex-wrap align-items-center gap-1') # зайнятість
                worked = worked_for.span.text
                region = worked_for.find('span', class_ = 'location-text').text

                description = job.find('span', class_ = 'js-truncated-text').text

                company = job.find('a', class_ = 'text-body js-analytics-event').text.strip()

                
                parsed_jobs.append({
                            'title': title,
                            'dependence': worked,
                            'company': company,
                            'information': info,
                            'address': region,
                            'description': description,
                            'date': data,
                            'link': link
                })

@router.message(F.text == 'IT Стажування')
async def cmd_start(message: Message):
    await message.answer("👋 Привіт! Я бот для пошуку вакансій з Djinni.co\n\n"
                        "Напишіть /interships щоб отримати останні IT-вакансій у Полтаві")

# Обробник команди /jobs
@router.message(Command("interships"))
async def cmd_jobs(message: Message):
    
    if not jobs:
        await message.answer("❌ Не вдалося отримати вакансії. Спробуйте пізніше.")
        return
    
    await message.answer(f"🔍 Знайдено {len(jobs)} вакансій. Готую інформацію...")
    
    for i, job in enumerate(parsed_jobs, 1):
        try:
            job_message = (
                        f"💻 <b>Робота:</b> #{i}\n"
                        f"🏢 <b>Компанія:</b> {job['company']}\n"
                        f"📊 <b>Інформація:</b> {job['information']}\n"
                        f"💼 <b>Посада:</b> {job['title']}\n"
                        f"💰 <b>Зайнятість:</b> {job['dependence']}\n"
                        f"📍 <b>Адреса:</b> {job['address']}\n"
                        f"📅 <b>Дата:</b> {job['date']}\n\n"
                        f"📝 <b>Опис:</b>\n{job['description']}\n\n"
                        f"🔗 <a href='{job['link']}'>Детальніше на djinni.co</a>"
                        )
            await message.answer(job_message, parse_mode="HTML")
            await asyncio.sleep(1)  # Пауза між повідомленнями
            
        except Exception as e:
            print(f"Помилка при відправці вакансії #{i}: {e}")

# Запуск бота
async def main():
    await router.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())