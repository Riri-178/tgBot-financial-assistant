from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import Database
from utils import create_pie_chart, create_forecast_chart
from aiogram import types
from keyboards import get_main_menu, get_categories_kb
import random
from keyboards import CATEGORIES, get_subcategories_kb, get_categories_kb
# from utils import generate_receipt_img
from datetime import datetime
from aiogram.utils.markdown import hbold, hitalic, hlink, hcode

router = Router()

GREETINGS = [
    "Привет! Рад тебя видеть!",
    "Здравствуй! Как дела?",
    "Йоу! С возвращением!",
    "Салют! Чем могу помочь?",
    "Добро пожаловать!",
    "Приветик! :)",
    "Здарова! Погнали!",
    "Хей! Как настроение?",
    "О, привет! Давно не виделись!",
    "Привет-привет!",
    "Здорово! Что нового?",
    "Привет! 👋",
    "Здравствуй! 😊",
    "Хей-хей! 🎉",
    "Салют! ✨",
    "Приветик! 🤗",
    "Здорова! 🚀",
    "Добро пожаловать! 🎈",
    "Привет, дружище! 🍻",
    "О, привет! 🌟",
    "Хаюшки! 🐣"
]

class ExpenseState(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_del_id = State()   
    waiting_for_subcategory = State()



@router.callback_query(F.data.startswith("maincat_"), StateFilter(ExpenseState.waiting_for_category))
async def process_main_category(callback: types.CallbackQuery, state: FSMContext):
    main_key = callback.data[8:]   # убираем "maincat_"
    main_data = CATEGORIES.get(main_key) # русское значение категории
    
    # Сохраняем основную категорию (если нужно)
    # сохраняем категорию, которую выбрал пользователь, чтобы знать, где мы
    await state.update_data(main_category=main_key, main_category_name=main_data["name"])
    
    # Показываем подкатегории
    subcats = main_data.get("subcategories", {}) # subcategories это ключ для словаря подкатегорий
    if subcats:
        kb = get_subcategories_kb(main_key, subcats)
        await callback.message.edit_text(f"Выберите подкатегорию для «{main_data['name']}»:", reply_markup=kb)
        await state.set_state(ExpenseState.waiting_for_subcategory) # режим ожидания выбора подкатегории от юзера 
    else:
        # Если подкатегорий нет, сразу переходим к вводу суммы
        await state.update_data(category=main_data["name"])
        await callback.message.edit_text(f"Выбрано: {main_data['name']}\nВведите сумму:")
        await state.set_state(ExpenseState.waiting_for_amount) # режим одижания суммы от юзера
    await callback.answer() # подтверждаем получение колбэка, чтобы у юзреа не висела загрузка кнопки(которую нажал)
                          

@router.callback_query(F.data.startswith("subcat_"), StateFilter(ExpenseState.waiting_for_subcategory))
async def process_subcategories(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.answer("Ошибка", show_alert=True)
        return
    main_key, sub_key = parts[1], parts[2]

    sub_name = CATEGORIES.get(main_key, {}).get("subcategories", {}).get(sub_key, "Другое")
    
    await state.update_data(category=sub_name)

    await callback.message.edit_text(f"Выбрано: {sub_name}\nВведите сумму:")
    await state.set_state(ExpenseState.waiting_for_amount)
    await callback.answer()

@router.callback_query(F.data == "back_to_main_cats")
async def back_to_main_categories(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseState.waiting_for_category)
    await callback.message.edit_text("Выберите категорию:", reply_markup=get_categories_kb())
    await callback.answer()



@router.message(Command("Help"))
@router.message(F.text == "Help")
async def cmd_help(message: Message):

    text = (
        
        f"Я бот для учёта расходов.\n"
        "Вот что я умею:\n"
        "➕ /add — добавить расход\n"
        "📊 /stats — статистика за всё время\n"
        "📈 /forecast — прогноз трат\n"
        "🗑 /del — удалить запись\n\n"
        "Используй кнопки внизу экрана."
    )

    await message.answer(text, parse_mode='HTML', reply_markup=get_main_menu())


@router.message(Command("start"))
async def cmd_start(message: Message):
    greeting = random.choice(GREETINGS)
    await message.answer(greeting, reply_markup=get_main_menu())


@router.message(F.text == "📅 Сегодня")
async def cmd_today(message: Message, db):
    expenses = await db.get_today(message.from_user.id)
    if not expenses:
        await message.answer('У вас нет записей на сегодня', reply_markup=get_main_menu())
    else:
        expense_list = "\n".join([f"{exp[2]}: {exp[3]} руб. ({exp[1]})" for exp in expenses])
        await message.answer(f"Ваши расходы:\n{expense_list}")    



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
    

# добавили новый хэндлер для категорий и подкатегорий этот больше не нужен
# @router.callback_query(F.data.startswith("cat_"), StateFilter(ExpenseState.waiting_for_category))
# async def process_category_callback(callback: types.CallbackQuery, state: FSMContext):
#     # Убираем префикс "cat_", чтобы получить чистое название категории
#     category_name = callback.data.split("_")[1]
    
#     await state.update_data(category=category_name)
    
#     # Редактируем старое сообщение, чтобы кнопки исчезли, или просто подтверждаем выбор
#     await callback.message.edit_text(f"Выбрана категория: {category_name}\nТеперь введите сумму:")
#     await state.set_state(ExpenseState.waiting_for_amount)
    
#     # Обязательно подтверждаем обработку callback, чтобы у юзера перестала "мигать" кнопка
#     await callback.answer()


# для чека
# @router.message(StateFilter(ExpenseState.waiting_for_amount))
# async def process_amount(message: Message, state: FSMContext, db):
#     data = await state.get_data()
#     category = data.get("category")
    
#     if not category:
#         await message.answer("❌ Ошибка: категория не найдена. Начните заново /add", reply_markup=get_main_menu())
#         await state.clear()
#         return
    
#     if not message.text.replace('.', '', 1).isdigit():
#         await message.answer("Пожалуйста, введите число (сумму).")
#         return


#     amount = float(message.text)
#     date_now = datetime.now().strftime("%d.%m.%Y %H:%M")

#     #  Записываем в базу
#     await db.add_expense(message.from_user.id, amount, category)
    
#     #  Генерируем "визуальный чек"
#     photo_bytes = generate_receipt_img(amount, category, date_now)
#     photo = BufferedInputFile(photo_bytes, filename="receipt.png")

#     #  Отправляем фото
#     await message.answer_photo(
#         photo=photo, 
#         caption=f"✅ Расход успешно записан!",
#         reply_markup=get_main_menu()
#     )
    
#     await state.clear()


# обычный(без чека)
@router.message(StateFilter(ExpenseState.waiting_for_amount))
async def process_amount(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    category = data.get("category")

    if not category:
        await message.answer("❌ Ошибка: категория не найдена. Начните заново /add", reply_markup=get_main_menu())
        await state.clear()
        return

    try:
        amount = (message.text.strip())
        if amount.find(','):
            amount = float(amount.replace(',', '.'))


        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except ValueError:
        await message.answer("❌ Ошибка: введите положительное число (например, 150.5)")
        # Не очищаем состояние, даём пользователю ещё одну попытку
        return

    # Сохраняем расход
    await db.add_expense(message.from_user.id, amount, category)
    await state.clear()
    await message.answer(
        f"✅ Расход в категории '{category}' на сумму {amount} руб. записан!",
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
    await message.answer(f"✅ Запись №{message.text} удалена.", reply_markup=get_main_menu())
    await state.clear() # Сбрасываем состояние 

    