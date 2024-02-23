from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F, Router
from config import DB_NAME
from keyboards.reg_keyboards import kb_request_contact, kb_register
from states.reg_states import RegisterStates
from datetime import date
from utils.database import Database

reg_router = Router()
db = Database(DB_NAME)


@reg_router.message(and_f(F.text == "Ro'yhatdan o'tish", RegisterStates.startReg))
async def reg_start(message: Message, state: FSMContext):
    await state.set_state(RegisterStates.fullname)
    await message.answer(text=f"To'liq familiya va ismingizni yuboring", reply_markup=ReplyKeyboardRemove())


@reg_router.message(RegisterStates.startReg)
async def reg(message: Message):
    await message.answer(text="Ro'yhatdan otish tugmasni bosing", reply_markup=kb_register)


@reg_router.message(RegisterStates.fullname)
async def reg_fullname(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RegisterStates.regPhone)
    await message.answer(text="telefon raqamingizni yuboring ", reply_markup=kb_request_contact)


@reg_router.message(RegisterStates.regPhone)
async def reg_phone(message: Message, state: FSMContext):
    try:
        await state.update_data(reg_phone=message.contact.phone_number)
        await message.answer(text="Email yuboring", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegisterStates.regEmail)
    except:
        await message.answer(f"Iltimos telefon raqamingizni yuboring tugmasni bosing")


@reg_router.message(RegisterStates.regEmail)
async def reg_email(message: Message, state: FSMContext):
    if message.text.endswith("@gmail.com"):
        await state.update_data(email=message.text)
        all_date = await state.get_data()
        x = db.add_user(
            u_id=message.from_user.id,
            fname=message.from_user.first_name,
            lname=message.from_user.last_name,
            fullname=all_date.get("full_name"),
            phone=all_date.get("reg_phone"),
            email=all_date.get("email"),
            date=date.today()
        )
        await state.clear()
        if x:
            await message.answer(text=f"ro'yxatdan muvaffaqitatli o'tinggiz")
        else:
            await message.answer(text=f"ro'yxatdan muvaffaqitatsiz o'tinggiz yana urnib ko'ring")
    else:
        await message.answer(text="iltimos email yuboring")