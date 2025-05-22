from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.keyboards import main
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Вітаю вас, Це бот створений для візуалізації даних і для того щоб слідкувати за IT всесвітом. Виберіть одну із опцій цього боту:",
        reply_markup=main
    )
    await state.clear()
    