from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    buttons = [
        [KeyboardButton(text="➕ Добавить расход"), KeyboardButton(text="🗑 Удалить запись")],
        [KeyboardButton(text="📊 Статистика (мес)"), KeyboardButton(text="📊 Статистика (всё)")],
        [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="📈 Прогноз")],
        [KeyboardButton(text="📄 Записи")]
    ]
    # resize_keyboard=True делает кнопки маленькими и аккуратными
    # input_field_placeholder — подсказка в поле ввода
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_categories_kb():
    # Создаем кнопки с callback_data, чтобы бот понял, на что нажали
    kb = [
        [
            InlineKeyboardButton(text="🍕 Еда", callback_data="cat_food"),
            InlineKeyboardButton(text="🚕 Такси", callback_data="cat_taxi")
        ],
        [
            InlineKeyboardButton(text="🏠 Жилье", callback_data="cat_home"),
            InlineKeyboardButton(text="🛒 Магазины(оффлайн)", callback_data="cat_shop")
        ],
        [
            InlineKeyboardButton(text="📱🖥️ Интернет", callback_data="cat_internet"),
            InlineKeyboardButton(text="Финансовая подушка", callback_data="cat_services")
        ],
        [
            InlineKeyboardButton(text="🏠 Wildberries", callback_data="cat_home"),
            InlineKeyboardButton(text="🛒 Ozon", callback_data="cat_shop")
        ],
        [
            InlineKeyboardButton(text="🏠 Кафе", callback_data="cat_home"),
            InlineKeyboardButton(text="🛒 Ресторан", callback_data="cat_shop")
        ],
        [
            InlineKeyboardButton(text="🏠 Жилье", callback_data="cat_home"),
            InlineKeyboardButton(text="🛒 Магазины", callback_data="cat_shop")
        ],     
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
     