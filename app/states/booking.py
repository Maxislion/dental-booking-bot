from aiogram.fsm.state import StatesGroup, State

class BookingState(StatesGroup):
    choosing_service = State()
    choosing_doctor = State()
    choosing_date = State()