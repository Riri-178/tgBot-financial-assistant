import matplotlib.pyplot as plt
import datetime
import io

def create_pie_chart(stats):
    # Разделяем данные на два списка: названия и значения
    categories = [row[0] for row in stats]
    amounts = [row[1] for row in stats]
    try:
        plt.figure(figsize=(8, 6))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title("Расходы по категориям")

        # Сохраняем график в "виртуальный файл" (буфер)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
    finally:
        plt.close() # Важно закрыть график, чтобы не тратить память
    return buffer



def create_forecast_chart(daily_data):
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