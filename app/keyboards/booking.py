from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def services_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🦷 Лечение кариеса", callback_data="service_caries")],
            [InlineKeyboardButton(text="🪥 Удаление зуба", callback_data="service_remove")],
            [InlineKeyboardButton(text="😁 Брекеты", callback_data="service_braces")],
        ]
    )
    
def dates_kb(offset: int = 0):
    keyboard = []

    today = datetime.today()

    dates = []
    for i in range(offset, offset + 6):  # 6 дат
        day = today + timedelta(days=i)
        date_str = day.strftime("%d.%m")
        dates.append(date_str)

    # делаем 2 колонки
    for i in range(0, len(dates), 2):
        row = []
        row.append(InlineKeyboardButton(text=dates[i], callback_data=f"date_{dates[i]}"))

        if i + 1 < len(dates):
            row.append(InlineKeyboardButton(text=dates[i+1], callback_data=f"date_{dates[i+1]}"))

        keyboard.append(row)

    # кнопки навигации
    keyboard.append([
        InlineKeyboardButton(text="⬅️", callback_data=f"nav_{max(offset-6, 0)}"),
        InlineKeyboardButton(text="➡️", callback_data=f"nav_{offset+6}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def time_kb(booked_times=None):
    if booked_times is None:
        booked_times = []

    times = [
        "10:00", "10:30",
        "11:00", "11:30",
        "12:00", "12:30",
        "14:00", "14:30",
        "15:00", "15:30"
    ]

    keyboard = []

    for i in range(0, len(times), 2):
        row = []

        for t in times[i:i+2]:
            if t in booked_times:
                # ❌ занято → показываем, но нельзя нажать
                row.append(
                    InlineKeyboardButton(text=f"❌ {t}", callback_data="busy")
                )
            else:
                row.append(
                    InlineKeyboardButton(text=t, callback_data=f"time_{t}")
                )

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_dates")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_booking")]
        ]
    )