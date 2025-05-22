from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='IT Зарплати'),
    KeyboardButton(text='Погода у вашому місті')],
    [KeyboardButton(text='IT Новини'),
    KeyboardButton(text='Курс криптовалют')],
    [KeyboardButton(text='IT Робота'),
    KeyboardButton(text='IT Стажування')],], resize_keyboard=True)