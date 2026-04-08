from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from database import Database
from utils import create_pie_chart, create_forecast_chart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from keyboards import get_main_menu, get_categories_kb

router = Router()

class ExpenseState(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_del_id = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет 😃",
                         reply_markup=get_main_menu()
                        )

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена") # Чтобы работало и на команду, и на текст
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.", reply_markup=get_main_menu())
        return

    await state.clear()
    await message.answer("Действие отменено.",
                         reply_markup=get_main_menu()
                        )  


@router.message(Command("add"))
@router.message(F.text == "➕ Добавить расход")
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("Введите категорию расхода(например: Еда, Такси):",
                         reply_markup=get_categories_kb()
                        )
    await state.set_state(ExpenseState.waiting_for_category)
    


@router.callback_query(F.data.startswith("cat_"), StateFilter(ExpenseState.waiting_for_category))
async def process_category_callback(callback: types.CallbackQuery, state: FSMContext):
    # Убираем префикс "cat_", чтобы получить чистое название категории
    category_name = callback.data.split("_")[1]
    
    await state.update_data(category=category_name)
    
    # Редактируем старое сообщение, чтобы кнопки исчезли, или просто подтверждаем выбор
    await callback.message.edit_text(f"Выбрана категория: {category_name}\nТеперь введите сумму:")
    await state.set_state(ExpenseState.waiting_for_amount)
    
    # Обязательно подтверждаем обработку callback, чтобы у юзера перестала "мигать" кнопка
    await callback.answer()

@router.message(StateFilter(ExpenseState.waiting_for_amount))
async def process_amount(message: Message, state: FSMContext, db):
    data = await state.get_data()
    amount = float(message.text)
    category = data.get("category")

    await db.add_expense(message.from_user.id, amount, category)
    await state.clear()  
    await message.answer(f"Расход в категории '{category}' на сумму {amount} записан!",
                         reply_markup=get_main_menu()
                        )
      
@router.message(Command("show"))
@router.message(F.text == "📄 Записи")
async def cmd_show(message: Message, db):
    expenses = await db.get_expenses(message.from_user.id)
    if not expenses:
        await message.answer("У вас нет записанных расходов.")
    else:
        expense_list = "\n".join([f"{expense[1]}: {expense[0]} ({expense[2]})" for expense in expenses])
        await message.answer(f"Ваши расходы:\n{expense_list}")


@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика (всё)")
async def cmd_stats(message: Message, db: Database):
    stats = await db.get_stats(message.from_user.id)
    
    if not stats:
        await message.answer("У вас еще нет данных для статистики.")
        return

    # 1. Генерируем график (лучше запустить в отдельном потоке, если данных много)
    # Но для начала сделаем прямо так:
    chart_buffer = create_pie_chart(stats)
    
    # 2. Обертываем буфер в объект, который понимает aiogram
    # Сначала получаем данные из буфера
    photo_data = chart_buffer.getvalue() 
    # Создаем файл
    photo = BufferedInputFile(photo_data, filename="stats.png")
    
    # 3. Отправляем пользователю
    await message.answer_photo(photo=photo, caption="📊 Ваша статистика расходов")

@router.message(Command("month"))
@router.message(F.text == "📊 Статистика (мес)")
async def cmd_stats_month(message: Message, db: Database):
    stats = await db.get_stats_month(message.from_user.id)
    
    if not stats:
        await message.answer("У вас еще нет данных для статистики.")
        return

    # 1. Генерируем график (лучше запустить в отдельном потоке, если данных много)
    # Но для начала сделаем прямо так:
    chart_buffer = create_pie_chart(stats)
    
    # 2. Обертываем буфер в объект, который понимает aiogram
    # Сначала получаем данные из буфера
    photo_data = chart_buffer.getvalue() 
    # Создаем файл
    photo = BufferedInputFile(photo_data, filename="stats.png")
    
    # 3. Отправляем пользователю
    await message.answer_photo(photo=photo, caption="📊 Ваша статистика расходов за месяц")


@router.message(Command("forecast"))
@router.message(F.text == "📈 Прогноз")
async def cmd_forecast(message: Message, db: Database):
    # Получаем данные за последние 20 дней
    daily_data = await db.get_daily_expenses(message.from_user.id, days=20)
    
    if len(daily_data) < 3:
        await message.answer("Мало данных для прогноза. Нужно хотя бы 3 дня с записями.")
        return

    chart_buffer = create_forecast_chart(daily_data)
    
    if chart_buffer:
        photo = BufferedInputFile(chart_buffer.getvalue(), filename="forecast.png")
        await message.answer_photo(
            photo=photo, 
            caption=f"📈 Прогноз на 10 дней.\nВаши средние траты: ~{sum(row[1] for row in daily_data)/len(daily_data):.2f} руб/день."
        )


# ЧАСТЬ 1: Выводим список и просим ID
@router.message(Command('del'))
@router.message(F.text == "🗑 Удалить запись")
async def cmd_del_start(message: Message, db: Database, state: FSMContext):
    data = await db.get_stats_text(message.from_user.id)
    if not data:
        await message.answer("У вас нет записей для удаления.")
        return

    text = "Выберите ID для удаления из списка выше или нажмите 'Отмена':\n\n"
    for item in data:
        text += f"🆔 {item[0]} | {item[2]}: {item[3]} руб.\n"

    # Можно создать временную клавиатуру только с отменой
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=cancel_kb)
    await state.set_state(ExpenseState.waiting_for_del_id)    

# ЧАСТЬ 2: Ловим введенный ID и удаляем
@router.message(StateFilter(ExpenseState.waiting_for_del_id))
async def cmd_del_confirm(message: Message, db: Database, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовой ID.")
        return

    await db.del_stat_text(message.from_user.id, int(message.text))
    await message.answer(f"✅ Запись №{message.text} удалена.")
    await state.clear() # Сбрасываем состояние 

    