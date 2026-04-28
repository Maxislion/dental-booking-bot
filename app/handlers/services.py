from aiogram import Router, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

router = Router()


@router.message(lambda msg: msg.text == "💰 Услуги и цены")
async def show_services(message: types.Message):
    text = (
        "💰 *Услуги и цены:*\n\n"
        "🦷 Лечение кариеса — от 200 000 сум\n"
        "🪥 Удаление зуба — от 150 000 сум\n"
        "😁 Брекеты — от 5 000 000 сум\n\n"
        "📍 Точная стоимость определяется после осмотра."
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📅 Записаться")],
                [KeyboardButton(text="💰 Услуги и цены")],
            ], resize_keyboard=True
        ),
    )
