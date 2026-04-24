from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер", request_contact=True)]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def start_handler(message: types.Message):
    text = (
        "👋 Добро пожаловать в *Bobur Denta!*\n\n"
        "Мы поможем вам получить здоровую и красивую улыбку 😊\n\n"
        "📍 Современное оборудование\n"
        "👨‍⚕️ Опытные стоматологи\n"
        "💯 Качественное лечение\n\n"
        "Чтобы записаться на прием, отправьте свой номер телефона 👇"
    )

    await message.answer(text, reply_markup=phone_kb, parse_mode="Markdown")


@router.message(lambda msg: msg.contact is not None)
async def get_contact(message: types.Message):
    phone = message.contact.phone_number

    await message.answer(
        f"✅ Спасибо! Ваш номер: {phone}\n\n"
        "Теперь вы можете записаться на прием 👇"
    )