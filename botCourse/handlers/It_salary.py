import logging
from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import io
import asyncio

from config import TOKEN

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація бота

bot = Bot(token=TOKEN)
router = Router()

# Список категорій
CATEGORIES = [
    "python", "javascript", "java", "ios"
]

def categories_inline_keyboard():
    keyboard = []
    # Додаємо по 2 кнопки в ряд
    for i in range(0, len(CATEGORIES), 2):
        row = []
        row.append(InlineKeyboardButton(text=CATEGORIES[i], callback_data=f"category_{CATEGORIES[i]}"))
        if i+1 < len(CATEGORIES):
            row.append(InlineKeyboardButton(text=CATEGORIES[i+1], callback_data=f"category_{CATEGORIES[i+1]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Функція для отримання текстової інформації
async def get_text_info(category):
    url = f'https://djinni.co/salaries/?category={category}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Інформація про кандидатів
    candidates_online = soup.find_all('div', class_ = 'col-sm-6 col-lg-4 mb-3')[0]
    candidates_title = candidates_online.a.div.div.h2.text.strip()
    candidates_count = candidates_online.find('span', class_ = 'fs-1').text.strip()
    candidates_last30 = candidates_online.find('span', class_ = 'text-diff text-danger') #dsafdfsa

    candidates_avg = candidates_online.find('div', class_='col-auto').text.strip().split()
    candidates_avg = f'{' '.join(candidates_avg)}'
    candidates_offers = candidates_online.find_all('div', class_='row')[1].find_all('small')[1].text
    candidates_offers = candidates_online.find_all('div', class_ = 'row')[1]
    candidates_offers = candidates_offers.find_all('small')[1].text
    
    # Інформація про вакансії
    vacancy_online = soup.find_all('div', class_='col-sm-6 col-lg-4 mb-3')[1]
    vacancy_title = vacancy_online.a.div.div.h2.text.strip()
    vacancy_count = vacancy_online.find('span', class_='fs-1').text.strip()
    # if category == "fullstack":
    #     vacancy_last30 = vacancy_online.find('span', class_='text-diff text-danger')
    vacancy_last30 = vacancy_online.find('span', class_='text-diff text-danger').span.text.strip() #sdfadfsa
    vacancy_avg = vacancy_online.find('div', class_='col-auto').text.strip().split()
    vacancy_avg = f'{' '.join(vacancy_avg)}'
    vacancy_offers = vacancy_online.find_all('div', class_='row')[1].find_all('small')[1].text.strip()
    
    text = (
        f"📊 <b>{candidates_title}</b>\n"
        f"👥 Всього кандидатів: <b>{candidates_count}</b>\n"
        # f"📈 За останні 30 днів: <b>{candidates_last30}</b>\n"
        f"💰 Середні очікування: <b>{candidates_avg}</b>\n"
        f"📩 Пропозицій в середньому: <b>{candidates_offers}</b>\n\n"
        f"💼 <b>{vacancy_title}</b>\n"
        f"📋 Всього вакансій: <b>{vacancy_count}</b>\n"
        # f"📈 За останні 30 днів: <b>{vacancy_last30}</b>\n"
        f"💰 Середня вилка: <b>{vacancy_avg}</b>\n"
        f"📩 Відгуків в середньому: <b>{vacancy_offers}</b>"
    )
    
    return text

# Функція для створення графіка очікувань кандидатів
async def create_candidates_chart(category):
    # Налаштування Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)  # 30 секунд на завантаження сторінки
        
        url = f"https://djinni.co/salaries/?category={category}"
        driver.get(url)
        await asyncio.sleep(5)
        
        page_html = driver.page_source
        if not page_html:
            raise ValueError("Не вдалося отримати вміст сторінки")

        soup = BeautifulSoup(page_html, 'html.parser')
        candidates_salaries = soup.find('section', id='candidates_salaries')
        
        title = candidates_salaries.find('div', class_='row justify-content-between lh-15 mb-2').div.h2.text.strip()
        salary_wait = candidates_salaries.find('div', class_='fs-1 fw-bold lh-125 mb-4').text.strip().split()
        salary_wait = f'{' '.join(salary_wait)}'
        
        chart_div = soup.find('div', {'id': 'average_candidate_expectations_chart'})
        value_salary = chart_div.find('g', class_='axis-x').find_all('g', class_='tick')
        value_salary_items = [value.text for value in value_salary]
        
        # Приклад даних (у реальному боті потрібно парсити точні значення)
        candidates_python = [173, 875, 588, 407, 341, 227, 170, 67, 44, 29, 4][:len(value_salary_items)]
        candidates_javascript = [589, 2785, 2336, 2093, 1676, 1182, 682, 313, 117, 62, 11][:len(value_salary_items)]
        candidates_java = [149, 654, 390, 518, 457, 467, 417, 222, 100, 45, 11][:len(value_salary_items)]
        candidates_ios = [15, 85, 123, 195, 190, 174, 114, 70, 19, 12, 3][:len(value_salary_items)]
        
        # Побудова графіка
        fig, ax = plt.subplots(figsize=(10, 5))
        if category == 'python':
            bars = ax.bar(value_salary_items, candidates_python, width=0.9, edgecolor='none', color='#3e8eff')
        elif category == 'javascript':
            bars = ax.bar(value_salary_items, candidates_javascript, width=0.9, edgecolor='none', color='#3e8eff')
        elif category == 'java':
            bars = ax.bar(value_salary_items, candidates_java, width=0.9, edgecolor='none', color='#3e8eff')
        else:
            bars = ax.bar(value_salary_items, candidates_ios, width=0.9, edgecolor='none', color='#3e8eff')
        
        ax.set_title(f'{title} {category}', fontsize=14, pad=20)
        fig.text(0.5, 0.9, f'${salary_wait}', fontsize=16, color='black', ha='center')
        ax.set_ylabel('Кількість кандидатів', fontsize=10)
        ax.set_xlabel('Діапазон зарплат', fontsize=10)
        
        ax.set_xticks(np.arange(len(value_salary_items)))
        ax.set_xticklabels(value_salary_items, fontsize=8)
        
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1)
            spine.set_edgecolor('black')
        
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        # Збереження графіка у буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        logger.error(f"Error creating chart for {category}: {e}")
        raise
    finally:
        if driver:
            driver.quit()

# Функція для створення графіка зарплат у вакансіях
async def create_vacancies_chart(category):
    # Налаштування Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = f"https://djinni.co/salaries/?category={category}"
        driver.get(url)
        await asyncio.sleep(5)
        page_html = driver.page_source
        
        soup = BeautifulSoup(page_html, 'html.parser')
        vacancy_salaries = soup.find('section', id='jobs_salaries')
        
        title = vacancy_salaries.find('h2', class_='fs-4 lh-15 fw-bold mb-0').a.text
        salary_wait = vacancy_salaries.find('div', class_='fs-1 fw-bold lh-125')
        salary_min = salary_wait.find_all('span')[0].text
        salary_max = salary_wait.find_all('span')[1].text
        salary_period = salary_wait.small.text
        
        chart_div = soup.find('div', {'id': 'jobs_salaries_chart'})
        value_salary = chart_div.find('g', class_='axis axis-x').find_all('g', class_='tick')
        months = [value.text for value in value_salary]
        
        # Приклад даних (у реальному боті потрібно парсити точні значення)
        # median_min = [int(salary_min)] * len(months)
        # median_max = [int(salary_max)] * len(months)
        # помінять для курсової median_min = salary_wait_min * len(months) 
        median_min_python = [2500] * len(months) 
        median_max_python = [4500] * len(months)
        median_min_javascript = [1500] * len(months) 
        median_max_javascript = [3000] * len(months)
        median_min_java = [3000] * len(months) 
        median_max_java = [5000] * len(months)
        median_min_ios = [2000] * len(months) 
        median_max_ios = [3400] * len(months)
        # hires_median = [int((int(salary_min) + int(salary_max))) / 2 * (0.8 + 0.4 * np.random.rand()) for _ in months]

        # помінять для курсової
        hires_median_python = [2500, 2000, 1400, 1300, 1700, 1400, 1200, 2000, 2900, 2000, 2550, 3000]
        hires_median_javascript = [2300, 2500, 2100, 1900, 2000, 1800, 2000, 2100, 1200, 2800, 1850, 2000]
        hires_median_java = [4000, 2000, 3000, 4400, 3400, 3000, 4000, 3000, 2500, 3000, 2000, 3250]
        hires_median_ios = [2500, 3000, 1500, 1800, 1600, 4350, 3800, 2250, 2000, 2600, 2700, 400]
        
        # Побудова графіка
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        if category == 'python':
            ax.fill_between(months, median_min_python, median_max_python, color='#dbe4f3', alpha=1.0, label='Медіанна зарплатна вилка')
        elif category == 'javascript':
            ax.fill_between(months, median_min_javascript, median_max_javascript, color='#dbe4f3', alpha=1.0, label='Медіанна зарплатна вилка')
        elif category == 'java':
            ax.fill_between(months, median_min_java, median_max_java, color='#dbe4f3', alpha=1.0, label='Медіанна зарплатна вилка')
        else:
            ax.fill_between(months, median_min_ios, median_max_ios, color='#dbe4f3', alpha=1.0, label='Медіанна зарплатна вилка')
        
        if category == 'python':
            ax.plot(months, hires_median_python, color='#3e8eff', marker='o', linewidth=2, label='Медіана зарплат найнятих')
        elif category == 'javascript':
            ax.plot(months, hires_median_javascript, color='#3e8eff', marker='o', linewidth=2, label='Медіана зарплат найнятих')
        elif category == 'java':
            ax.plot(months, hires_median_java, color='#3e8eff', marker='o', linewidth=2, label='Медіана зарплат найнятих')
        else:
            ax.plot(months, hires_median_ios, color='#3e8eff', marker='o', linewidth=2, label='Медіана зарплат найнятих')
        

        if category == 'python':
            ax.set_ylim(0, max(median_max_python) * 1.2)
        elif category == 'javascript':
            ax.set_ylim(0, max(median_max_javascript) * 1.2)
        elif category == 'java':
            ax.set_ylim(0, max(median_max_java) * 1.2)
        else:
            ax.set_ylim(0, max(median_max_ios) * 1.2)
        

        if category == 'python':
            ax.set_yticks(np.arange(0, max(median_max_python) * 1.2, max(median_max_python)/5))
        elif category == 'javascript':
            ax.set_yticks(np.arange(0, max(median_max_javascript) * 1.2, max(median_max_javascript)/5))
        elif category == 'java':
            ax.set_yticks(np.arange(0, max(median_max_java) * 1.2, max(median_max_java)/5))
        else:
            ax.set_yticks(np.arange(0, max(median_max_ios) * 1.2, max(median_max_ios)/5))
        
        if category == 'python':
            ax.set_yticklabels([f'{int(i)}' for i in np.arange(0, max(median_max_python) * 1.2, max(median_max_python)/5)],  fontsize=8)
        elif category == 'javascript':
            ax.set_yticklabels([f'{int(i)}' for i in np.arange(0, max(median_max_javascript) * 1.2, max(median_max_javascript)/5)],  fontsize=8)
        elif category == 'java':
            ax.set_yticklabels([f'{int(i)}' for i in np.arange(0, max(median_max_java) * 1.2, max(median_max_java)/5)],  fontsize=8)
        else:
            ax.set_yticklabels([f'{int(i)}' for i in np.arange(0, max(median_max_ios) * 1.2, max(median_max_ios)/5)],  fontsize=8)
        
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        
        for spine in ax.spines.values():
            spine.set_edgecolor('gray')
            spine.set_linewidth(1)
        
        plt.suptitle(f'{title} {category}', fontsize=14, fontweight='bold', y=0.95)
        ax.legend(loc='upper left', fontsize=8)
        
        plt.tight_layout()
        
        # Збереження графіка у буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    finally:
        driver.quit()


@router.message(F.text == 'IT Зарплати')
async def cmd_start(message: types.Message):
    await message.answer(
        "Вітаю! Цей бот показує статистику зарплат з Djinni.co\n"
        "Оберіть категорію з клавіатури:",
        reply_markup=categories_inline_keyboard()
    )

@router.callback_query(F.data.startswith("category_"))
async def handle_category_callback(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    
    try:
        # Спочатку відповідаємо на callback, щоб уникнути помилки "query is too old"
        await callback.answer()
        
        # Відправляємо повідомлення про обробку
        processing_msg = await callback.message.answer(f"🔍 Отримую дані для категорії {category}...")
        
        # Надсилання текстової інформації
        text_info = await get_text_info(category)
        await processing_msg.edit_text(text_info, parse_mode='HTML')
        
        # Надсилання першого графіка
        chart1_msg = await callback.message.answer("📈 Завантаження графіка очікувань кандидатів...")
        chart1 = await create_candidates_chart(category)
        await chart1_msg.delete()  # Видаляємо попереднє повідомлення
        await callback.message.answer_photo(
            types.BufferedInputFile(chart1.read(), filename="chart1.png"),
            caption="📈 Графік очікувань кандидатів"
        )
        
        # Надсилання другого графіка
        chart2_msg = await callback.message.answer("💼 Завантаження графіка зарплат у вакансіях...")
        chart2 = await create_vacancies_chart(category)
        await chart2_msg.delete()  # Видаляємо попереднє повідомлення
        await callback.message.answer_photo(
            types.BufferedInputFile(chart2.read(), filename="chart2.png"),
            caption="💼 Графік зарплат у вакансіях"
        )
        
    except Exception as e:
        logger.error(f"Error processing category {category}: {e}")
        await callback.message.answer(f"Виникла помилка при обробці категорії {category}. Спробуйте пізніше.")


# Запуск бота
async def main():
    await router.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())