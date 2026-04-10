from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

CATEGORIES = {
    "food": {
        "name": "🍕 Еда",
        "subcategories": {
            "groceries": "🛒 Продукты",
            "cafe": "☕ Кафе/Рестораны",
            "delivery": "🚚 Доставка еды",
        }
    },
    "transport": {
        "name": "🚗 Транспорт",
        "subcategories": {
            "taxi": "🚕 Такси",
            "public": "🚌 Общественный транспорт",
            "fuel": "⛽ Бензин",
        }
    },
    "home": {
        "name": "🏠 Жильё",
        "subcategories": {
            "rent": "🏢 Аренда",
            "utilities": "💡 Коммунальные услуги",
            "repair": "🔨 Ремонт",
        }
    },
    "medical expenses": {
        "name": "⚕️ Медицинские расходы",
        "subcategories": {
            "getting medical": "🏥 Поход к врачу",
            "medicines": "💊 Лекарства"
        }
    }, 

    "shopping": {
        "name": "🏬 Покупки в магазине",
        "subcategories": {
            "accessories": "💍 Аксессуары",
            "clothes": "🧣 Одежда",
            "furniture": "🪑 Элемент декора\мебель",
            "cosmetic": "💅 Косметика",
            "other": "Прочее"
        }
    },
    "marketplaces": {
        "name": " 🛍️ Маркетплейсы",
        "subcategories": {
            "accessories": "💍 Аксессуары",
            "clothes": "🧣 Одежда",
            "furniture": "🪑 Элемент декора\мебель",
            "cosmetic": "💅 Косметика",
            "other": "Прочее"
        }
    },
        "services": {
        "name": "📱 Услуги",
        "subcategories": {
            "Internet": "🌐 Интернет",
            "server rental": "🖥️ Аренда сервера",
            "other": "Прочее",
        }
    },
            "financial cushion": {
        "name": "Финансовая подушка",
        
    }         

}        
                






def get_main_menu():
    buttons = [
        [KeyboardButton(text="➕ Добавить расход"), KeyboardButton(text="🗑 Удалить запись")],
        [KeyboardButton(text="📊 Статистика (мес)"), KeyboardButton(text="📊 Статистика (всё)")],
        [KeyboardButton(text="📄 Записи"), KeyboardButton(text="📈 Прогноз")],
        [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="📅 Сегодня")],
        [ KeyboardButton(text="Help")]
    ]
    # resize_keyboard=True делает кнопки маленькими и аккуратными
    # input_field_placeholder — подсказка в поле ввода
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_categories_kb():
    buttons = []
    row = []
    for key, data in CATEGORIES.items():
        row.append(InlineKeyboardButton(
            text=data["name"],
            callback_data=f"maincat_{key}"   # префикс maincat_
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)    



def get_subcategories_kb(main_key, subcategories_dict):
    buttons = []
    row = []
    for sub_key, sub_name in subcategories_dict.items():
        # callback_data: subcat_<mainKey>_<subKey>
        callback_data = f"subcat_{main_key}_{sub_key}"
        row.append(InlineKeyboardButton(text=sub_name, callback_data=callback_data))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    # Добавляем кнопку "Назад" к основным категориям
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main_cats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# def get_categories_kb():
#     # Создаем кнопки с callback_data, чтобы бот понял, на что нажали
#     kb = [
#         [
#             InlineKeyboardButton(text="🍕 Еда", callback_data="cat_food"),
#             InlineKeyboardButton(text="🚕 Такси", callback_data="cat_taxi")
#         ],
#         [
#             InlineKeyboardButton(text="🏠 Жилье", callback_data="cat_home"),
#             InlineKeyboardButton(text="🛒 Магазины(оффлайн)", callback_data="cat_shop")
#         ],
#         [
#             InlineKeyboardButton(text="📱🖥️ Интернет", callback_data="cat_internet"),
#             InlineKeyboardButton(text="Финансовая подушка", callback_data="cat_services")
#         ],
#         [
#             InlineKeyboardButton(text="🏠 Wildberries", callback_data="cat_home"),
#             InlineKeyboardButton(text="🛒 Ozon", callback_data="cat_shop")
#         ],
#         [
#             InlineKeyboardButton(text="🏠 Кафе", callback_data="cat_home"),
#             InlineKeyboardButton(text="🛒 Ресторан", callback_data="cat_shop")
#         ],
#         [
#             InlineKeyboardButton(text="🏠 Жилье", callback_data="cat_home"),
#             InlineKeyboardButton(text="🛒 Магазины", callback_data="cat_shop")
#         ],     
#     ]
#     return InlineKeyboardMarkup(inline_keyboard=kb)
     