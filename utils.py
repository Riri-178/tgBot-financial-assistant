import matplotlib.pyplot as plt
import datetime
import io
import asyncio



# для чека
# from html2image import Html2Image
# import io

# h2i = Html2Image(
#     browser_executable='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
#     custom_flags=['--no-sandbox', '--disable-gpu', '--hide-scrollbars']
# )

# def generate_receipt_img(amount, category, date):
#     # Наш HTML-шаблон со стилями «под чек»
#     html_content = f"""
#     <div class="receipt">
#         <h1 style="text-align:center;">💰 ФИНАНСОВЫЙ ЧЕК 💰</h1>
#         <hr>
#         <p><b>Дата:</b> {date}</p>
#         <p><b>Категория:</b> {category}</p>
#         <p><b>Сумма:</b> <span class="amount">{amount} руб.</span></p>
#         <hr>
#         <p style="text-align:center; font-style:italic;">Спасибо, что следите за бюджетом!</p>
#     </div>
    
#     <style>
#         .receipt {{
#             background-color: #fff;
#             padding: 20px;
#             width: 300px;
#             font-family: 'Courier New', Courier, monospace;
#             border: 1px solid #ddd;
#         }}
#         .amount {{
#             font-size: 24px;
#             color: #2e7d32;
#         }}
#         hr {{ border: 1px dashed #ccc; }}
#     </style>
#     """
    
#     # Генерируем изображение в файл, а затем читаем его в буфер
#     # (html2image сохраняет файл временно на диск)
#     h2i.screenshot(html_str=html_content, save_as='receipt.png', size=(350, 450))
    
#     with open('receipt.png', 'rb') as f:
#         return f.read()








def create_pie_chart_sync(stats):
    # stats — это список кортежей [(сумма, категория), ...]
    categories = [item[0] for item in stats] # Теперь тут 'accessories'
    amounts = [item[1] for item in stats]    # А тут число

    # Увеличиваем ширину фигуры (10), чтобы справа поместилась легенда
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    # Рисуем сам пирог
    # labels=None убирает подписи прямо с круга
    # pctdistance=0.85 смещает проценты чуть ближе к краю для красоты
    wedges, texts, autotexts = ax.pie(
        amounts, 
        autopct='%1.1f%%', 
        startangle=140, 
        pctdistance=0.75,
        colors=plt.cm.Pastel1.colors # Используем мягкие пастельные цвета
    )

    # Настройка шрифта процентов (делаем их меньше, чтобы не слипались)
    plt.setp(autotexts, size=9, weight="bold")

    # Добавляем легенду
    ax.legend(
        wedges, 
        categories,
        title="Категории",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1), # Выносим легенду за пределы круга вправо
        fontsize=10,
        frameon=False # Убираем рамку вокруг легенды для чистоты
    )

    ax.set_title("Распределение расходов", pad=20, size=14)

    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight') # bbox_inches='tight' сохранит легенду целиком
    buf.seek(0)
    plt.close(fig) # Обязательно закрываем фигуру, чтобы не забивать память сервера
    
    return buf


async def create_pie_chart(stats):
    return await asyncio.to_thread(create_pie_chart_sync, stats)


def create_forecast_chart_sync(daily_data):
    # 1. Подготовка данных
    dates = [row[0] for row in daily_data]
    amounts = [row[1] for row in daily_data]
    
    if not amounts:
        return None

    # Вычисляем среднее значение трат в день
    avg_expense = sum(amounts) / len(amounts)
    
    try:

        # Создаем оси для прогноза (следующие 10 дней)
        last_date = datetime.datetime.strptime(dates[-1], '%Y-%m-%d')
        forecast_dates = [(last_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 11)]
        forecast_amounts = [avg_expense] * 10

        # 2. Рисование
        plt.figure(figsize=(10, 5))
        
        # Реальные данные (сплошная линия)
        plt.plot(dates, amounts, marker='o', label='Реальные траты', color='blue')
        
        # Прогноз (пунктирная линия)
        # Соединяем последнюю реальную точку с первой точкой прогноза
        plt.plot([dates[-1]] + forecast_dates, [amounts[-1]] + forecast_amounts, 
                linestyle='--', color='red', label='Прогноз (среднее)')

        plt.title("Прогноз трат на ближайшие 10 дней")
        plt.xlabel("Дата")
        plt.ylabel("Сумма (руб)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

    finally:   
        plt.close()
    return buffer


async def create_forecast_chart(stats):
    return await asyncio.to_thread(create_forecast_chart_sync, stats)

