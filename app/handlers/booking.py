from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.keyboards.booking import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.repositories.booking_repo import *
from app.utils.config import ADMIN_ID

from app.states.booking import BookingState

router = Router()


@router.message(lambda msg: msg.text == "📅 Записаться")
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(BookingState.choosing_service)

    await message.answer("Выберите услугу:", reply_markup=services_kb())


doctors = {
    "service_caries": [
        {
            "id": "doc_1",
            "name": "Др. Алиев",
            "desc": "Терапевт, 5 лет опыта",
            "photo": "https://via.placeholder.com/300",
        },
        {
            "id": "doc_2",
            "name": "Др. Каримова",
            "desc": "Стоматолог-ортодонт",
            "photo": "https://via.placeholder.com/300",
        },
    ],
    "service_remove": [
        {
            "id": "doc_3",
            "name": "Др. Ахмедов",
            "desc": "Хирург, удаление любой сложности",
            "photo": "https://via.placeholder.com/300",
        }
    ],
    "service_braces": [
        {
            "id": "doc_4",
            "name": "Др. Юсупова",
            "desc": "Брекеты и выравнивание зубов",
            "photo": "https://via.placeholder.com/300",
        }
    ],
}


def doctor_kb(doc_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выбрать", callback_data=f"doctor_{doc_id}")]
        ]
    )


@router.callback_query(lambda c: c.data.startswith("service_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data

    await state.update_data(service=service)

    docs = doctors.get(service, [])

    if not docs:
        await callback.message.answer("Нет доступных врачей")
        return

    for doc in docs:
        text = f"👨‍⚕️ {doc['name']}\n" f"{doc['desc']}"

        await callback.message.answer_photo(
            photo=doc["photo"], caption=text, reply_markup=doctor_kb(doc["id"])
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("doctor_"))
async def choose_doctor(callback: CallbackQuery, state: FSMContext):
    doctor_id = callback.data.replace("doctor_", "")

    # найти врача по id
    doctor_name = "Неизвестный врач"

    for service_docs in doctors.values():
        for doc in service_docs:
            if doc["id"] == doctor_id:
                doctor_name = doc["name"]

    await state.update_data(doctor=doctor_id, doctor_name=doctor_name)
    await state.set_state(BookingState.choosing_date)

    await callback.message.answer(
        f"👨‍⚕️ Вы выбрали: {doctor_name}\n\n📅 Выберите дату:", reply_markup=dates_kb(0)
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.replace("date_", "")

    data = await state.get_data()
    doctor = data.get("doctor_name")

    await state.update_data(date=date)

    # 🔥 получаем занятые слоты
    booked_times = await get_booked_times(doctor, date)

    text = f"👨‍⚕️ Вы выбрали: {doctor}\n" f"📅 Дата: {date}\n\n" "⏰ Выберите время:"

    await callback.message.edit_text(text, reply_markup=time_kb(booked_times))

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.replace("time_", "")

    data = await state.get_data()

    doctor = data.get("doctor_name")
    date = data.get("date")

    await state.update_data(time=time)

    text = (
        "Проверьте данные перед подтверждением:\n\n"
        f"👨‍⚕️ Врач: {doctor}\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}"
    )

    await callback.message.edit_text(text, reply_markup=confirm_kb())

    await callback.answer()


@router.callback_query(lambda c: c.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = (
        f"@{callback.from_user.username}"
        if callback.from_user.username
        else callback.from_user.full_name or f"ID: {callback.from_user.id}"
    )

    doctor = data.get("doctor_name")
    date = data.get("date")
    time = data.get("time")

    user_id = callback.from_user.id

    # 🔥 проверка занятости
    booked_times = await get_booked_times(doctor, date)
    if time in booked_times:
        await callback.answer(
            "Это время уже заняли. Выберите другое ❌", show_alert=True
        )
        return

    # 💾 сохраняем
    await create_booking(user_id, doctor, date, time)

    # ✅ 1. ОТВЕТ ПОЛЬЗОВАТЕЛЮ (ВАЖНО)
    await callback.message.edit_text(
        f"⏳ Заявка отправлена!\n\n"
        f"👨‍⚕️ Врач: {doctor}\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}\n\n"
        "Пожалуйста, ожидайте подтверждение."
    )

    # 🔔 2. УВЕДОМЛЕНИЕ АДМИНУ
    await callback.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📢 Новая запись!\n\n"
            f"👤 Пользователь: {user}\n"
            f"👨‍⚕️ Врач: {doctor}\n"
            f"📅 Дата: {date}\n"
            f"⏰ Время: {time}"
        ),
        reply_markup=admin_confirm_kb(callback.from_user.id, doctor, date, time),
    )

    await state.clear()
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_confirm"))
async def admin_confirm(callback: CallbackQuery):
    _, user_id, doctor, date, time = callback.data.split("|")

    user_id = int(user_id)

    await callback.bot.send_message(
        chat_id=user_id,
        text=(
            "<b>✅ Ваша запись подтверждена!</b>\n\n"
            f"👨‍⚕️ Врач: {doctor}\n"
            f"📅 Дата: {date}\n"
            f"⏰ Время: {time}\n\n"
            "📍 Boburdenta, Ташкент, Сергелийский район\n"
            "<b>Пожалуйста, приходите за 5–10 минут до приема.</b>"
        ), parse_mode="HTML"
    )

    # 📍 отправляем геолокацию
    await callback.bot.send_location(
        chat_id=user_id, latitude=41.212546, longitude=69.236330
    )

    await callback.answer("Подтверждено")


@router.callback_query(lambda c: c.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_reject_", ""))

    await callback.bot.send_message(
        chat_id=user_id,
        text="❌ К сожалению, выбранное время недоступно. Попробуйте другое.",
    )

    await callback.answer("Отклонено")

@router.message(lambda msg: msg.text == "/records")
async def show_today_records(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    bookings = await get_today_bookings()

    if not bookings:
        await message.answer("📋 Сегодня записей нет")
        return

    text = "📋 Записи на сегодня:\n\n"

    for i, booking in enumerate(bookings, 1):
        user_id, doctor, date, time = booking

        text += (
            f"{i}. 👨‍⚕️ {doctor}\n"
            f"⏰ {time}\n"
            f"👤 ID: {user_id}\n\n"
        )

    await message.answer(text)


@router.callback_query(lambda c: c.data == "edit_booking")
async def edit_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    doctor_name = data.get("doctor_name")

    await callback.message.edit_text(
        f"👨‍⚕️ Вы выбрали: {doctor_name}\n\n📅 Выберите дату:", reply_markup=dates_kb()
    )

    await state.set_state(BookingState.choosing_date)

    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    doctor_name = data.get("doctor_name", "Врач")

    await state.set_state(BookingState.choosing_date)

    await callback.message.edit_text(
        f"👨‍⚕️ Вы выбрали: {doctor_name}\n\n📅 Выберите дату:", reply_markup=dates_kb()
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("nav_"))
async def navigate_dates(callback: CallbackQuery):
    offset = int(callback.data.replace("nav_", ""))

    await callback.message.edit_reply_markup(reply_markup=dates_kb(offset))

    await callback.answer()


@router.callback_query(lambda c: c.data == "busy")
async def busy_time(callback: CallbackQuery):
    await callback.answer("Это время уже занято ❌", show_alert=True)
