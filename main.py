import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import os
import aiosqlite  
import secrets
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from handlers import router
from database import Database

async def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )


async def main():

    await set_logging()
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    bot = Bot(token=token)  
    dp = Dispatcher()
    db = Database('expenses.db')


    await db.setup()
    
    dp.include_router(router)


    await dp.start_polling(bot, db=db)





if __name__ == "__main__":
    asyncio.run(main())

