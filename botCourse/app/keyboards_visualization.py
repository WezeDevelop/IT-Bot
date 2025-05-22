from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


chart_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Лінійний графік")],
        [KeyboardButton(text="Стовпчикова діаграма")] # [KeyboardButton(text="Кругова діаграма")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Оберіть тип діаграми"
)
