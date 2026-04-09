import asyncio
import logging
import os
import aiosqlite  
import secrets
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv
from handlers import router
from database import Database
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable





async def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )


class DbMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db 

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any]
    ) -> Any:
       
        db = Database('expenses.db')
        await db.setup()
        data['db'] = db
        return await handler(event, data)


async def main():

    await set_logging()
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    bot = Bot(token=token)  
    dp = Dispatcher()
    db = Database('expenses.db')


    dp.message.middleware(DbMiddleware(db))
    dp.callback_query.middleware(DbMiddleware(db))
    
    dp.include_router(router)


    await dp.start_polling(bot)





if __name__ == "__main__":
    asyncio.run(main())

