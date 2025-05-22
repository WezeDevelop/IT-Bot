import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

from config import TOKEN

# Налаштування бота
bot = Bot(token=TOKEN)
router = Router()

# Функція для парсингу статей
def parse_articles():
    url = "https://proit.ua/tag/articles/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('div', class_='site-post-card articles')[:5]
    
    parsed_articles = []
    for article in articles:
        try:
            title = article.find('a', class_='site-post-card-title').text.strip()
            author = article.find('div', class_='site-post-card-additional-info').a.span.text.strip()
            description = article.find('p', class_='site-post-card-text').text.strip()
            link_article_main = article.find('a', class_='site-post-card-img')['href']
            link_article = f'https://proit.ua{link_article_main}'
            date = article.find('div', class_='site-post-card-date').time.text.strip()
            
            parsed_articles.append({
                'title': title,
                'author': author,
                'description': description,
                'date': date,
                'link': link_article
            })
        except Exception as e:
            print(f"Помилка при парсингу: {e}")
    
    return parsed_articles


@router.message(F.text == 'IT Новини')
async def cmd_start(message: Message):
    await message.answer("Привіт! Я бот для отримання статей з proit.ua\nНапиши /articles щоб отримати 5 останніх статей")

# Обробник команди /articles
@router.message(Command("articles"))
async def cmd_articles(message: Message):
    articles = parse_articles()
    
    if not articles:
        await message.answer("Не вдалося отримати статті. Спробуйте пізніше.")
        return
    
    await message.answer(f"🔄 Знайдено {len(articles)} статей. Готую до відправки...")
    
    for i, article in enumerate(articles, 1):
        try:
            article_text = (
                f"📌 <b>Стаття #{i}</b>\n\n"
                f"📚 <b>Назва:</b> {article['title']}\n"
                f"✍️ <b>Автор:</b> {article['author']}\n"
                f"📅 <b>Дата:</b> {article['date']}\n\n"
                f"📝 <b>Опис:</b>\n{article['description']}\n\n"
                f"🔗 <a href='{article['link']}'>Читати повністю</a>"
            )
            
            await message.answer(article_text, parse_mode="HTML")
            await asyncio.sleep(1)  # Невелика затримка між повідомленнями
        except Exception as e:
            print(f"Помилка при відправці статті #{i}: {e}")

# Запуск бота
async def main():
    await router.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())