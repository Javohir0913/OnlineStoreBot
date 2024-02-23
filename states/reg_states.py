from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    startReg = State()
    fullname = State()
    regPhone = State()
    regEmail = State()
    regDate = State()



