from config import TOKEN
import logging
import numpy as np

import app.keyboards_visualization as kb

import os
import pandas as pd
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio


# Налаштування бота
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Кеш для збереження даних користувачів
data_cache = {}

# Стан машини станів (FSM)
class ChartStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_chart_type = State()
    waiting_for_column = State()  

# Обробка команди Візуалізація даних
@router.message(lambda message: message.text == "Візуалізація даних")
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Привіт! Надішли мені файл у форматі CSV або XLS.")
    await state.set_state(ChartStates.waiting_for_file)

# Обробка отриманого файлу
@router.message(lambda message: message.document, ChartStates.waiting_for_file)
async def handle_file(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_path = f"downloads/{file_name}"

    os.makedirs("downloads", exist_ok=True)

    file = await bot.get_file(file_id)
    await bot.download(file, destination=file_path)

    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            await message.answer("Формат файлу не підтримується. Надішліть CSV або XLS.")
            return
    except Exception as e:
        await message.answer(f"Помилка при зчитуванні файлу: {e}")
        return

    # Збереження даних користувача
    data_cache[message.chat.id] = df
    await message.answer("Файл отримано! Який тип діаграми ви хочете побудувати?", reply_markup=kb.chart_keyboard)
    await state.set_state(ChartStates.waiting_for_chart_type)

# Обробка вибору типу діаграми
@router.message(lambda message: message.text in ["Лінійний графік", "Стовпчикова діаграма"], ChartStates.waiting_for_chart_type) #"Кругова діаграма"
async def handle_chart_type(message: types.Message, state: FSMContext):
    df = data_cache.get(message.chat.id)
    if df is None:
        await message.answer("Будь ласка, надішліть файл ще раз.")
        return

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_columns:
        await message.answer("У файлі немає числових стовпців. Надішліть інший файл.")
        return

    # Зберігаємо вибір користувача
    await state.update_data(chart_type=message.text)

    # Створюємо клавіатуру з доступними числовими стовпцями
    column_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=col)] for col in numeric_columns],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Оберіть числовий стовпець"
)

    await message.answer("Оберіть числовий стовпець для побудови діаграми:", reply_markup=column_keyboard)
    await state.set_state(ChartStates.waiting_for_column)

# Обробка вибору стовпця
@router.message(lambda message: message.text, ChartStates.waiting_for_column)
async def handle_column_choice(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chart_type = user_data.get("chart_type")
    df = data_cache.get(message.chat.id)

    if df is None or message.text not in df.columns:
        await message.answer("Оберіть правильний стовпець із запропонованих.")
        return

    column_name = message.text
    
    plt.figure()

    # Видаляємо NaN і перевіряємо, чи є взагалі дані
    values = df[column_name].dropna()
    if values.empty:
        await message.answer("У вибраному стовпці немає числових даних!")
        return

    # Перетворюємо індекси на числові, щоб уникнути проблем
    values = values.reset_index(drop=True)

    # Визначаємо 4 середні значення
    num_values = len(values)
    if num_values >= 4:
        middle_indices = list(range(num_values // 2 - 2, num_values // 2 + 2))
    else:
        middle_indices = list(range(num_values))  # Якщо менше 4 значень, беремо всі

    middle_values = values.iloc[middle_indices]

    

    plt.figure(figsize=(8, 6))

    if chart_type == "Лінійний графік":
        plt.plot(values, marker="o", linestyle="-", markersize=4)
    elif chart_type == "Стовпчикова діаграма":
        plt.bar(range(len(values)), values)
    else:
        await message.answer("Невідомий тип графіка.")
        return

    # Додаємо заголовок графіку для кращої наочності
    plt.title(f"{chart_type} для {column_name}")

    values = values.sort_values().reset_index(drop=True)


    # Прибираємо зайві підписи всередині графіка
    plt.gca().get_yaxis().set_visible(True)  # Лишаємо тільки вісь Y
    plt.gca().get_xaxis().set_visible(True)  # Лишаємо тільки вісь X

    plt.xticks(
    ticks=np.linspace(0, len(values) - 1, num=4, dtype=int),  # 4 рівномірні мітки
    labels=[f"{values.iloc[int(i)]:.2f}" for i in np.linspace(0, len(values) - 1, num=4)]
)
    
    # Видаляємо підписи значень із самого графіка
    plt.gca().get_yaxis().set_visible(True)  # Залишаємо тільки підписані значення на осі Y

    img_path = f"downloads/chart_{message.chat.id}.png"
    plt.savefig(img_path)
    plt.close()

    img = FSInputFile(img_path)
    await message.answer_photo(img, caption=f"Ось ваша {chart_type.lower()} для '{column_name}'!")

    await state.clear()
    os.remove(img_path)

# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
