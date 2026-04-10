import aiosqlite
import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

import logging
import aiosqlite
import datetime

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def setup(self):
        """Создаёт таблицу, если её нет. Логирует ошибки."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        category TEXT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await db.commit()
                logger.info("База данных инициализирована (таблица expenses проверена/создана)")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}", exc_info=True)
            raise  # Перебрасываем исключение, чтобы бот не запустился без БД

    async def add_expense(self, user_id, amount, category):
        """Добавляет расход. Возвращает True при успехе, иначе False."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
                    (user_id, amount, category)
                )
                await db.commit()
                logger.debug(f"Добавлен расход: user={user_id}, amount={amount}, cat={category}")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления расхода (user={user_id}, amount={amount}, cat={category}): {e}", exc_info=True)
            return False

    async def get_expenses(self, user_id):
        """Возвращает список расходов или пустой список при ошибке."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    'SELECT amount, category, date, id FROM expenses WHERE user_id = ? ORDER BY date DESC',
                    (user_id,)
                )
                expenses = await cursor.fetchall()
                logger.debug(f"Получено {len(expenses)} записей для user={user_id}")
                return expenses
        except Exception as e:
            logger.error(f"Ошибка получения расходов для user={user_id}: {e}", exc_info=True)
            return []  # возвращаем пустой список, чтобы бот не падал

    async def get_stats(self, user_id):
        """Возвращает статистику (категория, сумма) или пустой список."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
                    (user_id,)
                )
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения статистики для user={user_id}: {e}", exc_info=True)
            return []

    async def get_stats_month(self, user_id):
        """Статистика за текущий месяц."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                now = datetime.datetime.now()
                cursor = await db.execute(
                    """
                    SELECT category, SUM(amount) 
                    FROM expenses 
                    WHERE user_id = ? AND strftime('%Y-%m', date) = ?
                    GROUP BY category
                    """,
                    (user_id, now.strftime('%Y-%m'))
                )
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения статистики за месяц для user={user_id}: {e}", exc_info=True)
            return []

    async def get_daily_expenses(self, user_id, days=20):
        """Суммы трат по дням для прогноза."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT date(date), SUM(amount)
                    FROM expenses
                    WHERE user_id = ? AND date >= date('now', ?) AND category NOT IN ('Финансовая подушка')
                    GROUP BY date(date)
                    ORDER BY date(date) ASC
                    """,
                    (user_id, f'-{days} days')
                )
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения дневных трат для user={user_id}: {e}", exc_info=True)
            return []

    async def get_stats_text(self, user_id):
        """Список записей с id, датой, категорией, суммой для удаления."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT id, date(date), category, amount
                    FROM expenses
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения текстовой статистики для user={user_id}: {e}", exc_info=True)
            return []

    async def del_stat_text(self, user_id, expense_id):
        """Удаляет запись по id и user_id. Возвращает True, если удалено, иначе False."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM expenses WHERE user_id = ? AND id = ?",
                    (user_id, expense_id)
                )
                await db.commit()
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Удалена запись id={expense_id} для user={user_id}")
                else:
                    logger.warning(f"Попытка удалить несуществующую запись id={expense_id} для user={user_id}")
                return deleted
        except Exception as e:
            logger.error(f"Ошибка удаления записи id={expense_id} для user={user_id}: {e}", exc_info=True)
            return False


    async def get_today(self, user_id):
        try:
            async with aiosqlite.connect(self.db_path) as db:

                cursor = await db.execute("""
                                    SELECT id, date(date), category, amount
                                    FROM expenses
                                    WHERE user_id = ? AND DATE(date) = DATE('now')
                                    """,
                                    (user_id,)
                                    )
                return await cursor.fetchall()
            
        except Exception as e:
                logging.warning(f"Ошибка при получении записей на сегодня: {e}")
                return []
        
   

                                    






