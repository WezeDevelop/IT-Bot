from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import logging
from config import TOKEN


# from handlers.visualization import router as visualization_router
from handlers.start import router as start_router
from handlers.find_weather_bot import router as weather_router
from handlers.Crypto import router as crypto_router
from handlers.articles import router as articles_router
from handlers.parsingjobs import router as jobs_router
from handlers.parsingInterships import router as interships_router
from handlers.It_salary import router as salary_router



async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    
    dp.include_router(start_router)
    dp.include_router(salary_router)
    dp.include_router(crypto_router)
    dp.include_router(articles_router)
    dp.include_router(jobs_router)
    dp.include_router(interships_router)
    dp.include_router(weather_router)

    await dp.start_polling(bot)
    



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')



