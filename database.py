import aiosqlite
import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def setup(self):
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

    async def add_expense(self, user_id, amount, category):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
                (user_id, amount, category)
            )
            await db.commit()


    async def get_expenses(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT amount, category, date, id FROM expenses WHERE user_id = ? ORDER BY date DESC',
                (user_id,)
            )
            expenses = await cursor.fetchall()
            return expenses    
        

    async def get_stats(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            # Группируем расходы по категориям и считаем сумму для каждой
            cursor = await db.execute(
                "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
                (user_id,)
            )
            return await cursor.fetchall()
        

    async def get_stats_month(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            # 1. Определяем первый день текущего месяца (например, '2026-04-01')
            now = datetime.datetime.now()
            first_day_of_month = now.strftime('%Y-%m-01 00:00:00')

            # 2. SQL запрос с фильтром по дате и user_id
            cursor = await db.execute(
                """
                SELECT category, SUM(amount) 
                FROM expenses 
                WHERE user_id = ? AND date >= ?
                GROUP BY category
                """,
                (user_id, first_day_of_month)
            )
            return await cursor.fetchall()   
        
    async def get_daily_expenses(self, user_id, days=20):
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем сумму трат за каждый из последних 20 дней
            cursor = await db.execute(
                """
                SELECT date(date), SUM(amount)
                FROM expenses
                WHERE user_id = ? AND date >= date('now', ?)
                GROUP BY date(date)
                ORDER BY date(date) ASC
                """,
                (user_id, f'-{days} days')
            )
            return await cursor.fetchall()        
    
    async def get_stats_text(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''
                SELECT id, date(date), category, amount
                FROM expenses
                WHERE user_id = ? 
                ''',
                (user_id,)

            )
            expenses = await cursor.fetchall()
            return expenses   
        

    async def del_stat_text(self, user_id, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''
                DELETE FROM expenses
                WHERE user_id = ? AND id = ?
                ''',
                (user_id, value)
            )   
            await db.commit()



