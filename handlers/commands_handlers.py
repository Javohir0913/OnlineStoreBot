from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.admin_inline_keyboards import make_category_list, yes_or_no
from states.admin_states import CategoryStates
from utils.database import Database
from utils.my_commands import commands_admin, commands_user

commands_router = Router()
db = Database(DB_NAME)


@commands_router.message(CommandStart())
async def start_handler(message: Message):
    if message.from_user.id in admins:
        await message.bot.set_my_commands(commands=commands_admin)
        await message.answer("Welcome admin, please choose command from commands list")
    else:
        await message.bot.set_my_commands(commands=commands_user)
        await message.answer("Let's start registration")


@commands_router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("All actions canceled, you may continue sending commands")


# With this handler admin can add new category
@commands_router.message(Command('new_category'))
async def new_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.newCategory_state)
    await message.answer("Please, send new category name ...")


# Functions for editing category name
@commands_router.message(Command('edit_category'))
async def edit_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.updCategory_state_list)
    await message.answer(
        text="Choose category name which you want to change...",
        reply_markup=make_category_list()
    )


@commands_router.message(Command("del_category"))
async def del_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.delCategory_state)
    await message.answer(text=f"Qaysi kategoriyani o'chirmochisiz", reply_markup=make_category_list())


@commands_router.callback_query(CategoryStates.delCategory_state)
async def callback_category_del(callback: CallbackQuery, state: FSMContext):
    await state.update_data(del_name=callback.data)
    await state.set_state(CategoryStates.delCategory_state1)
    await callback.message.delete()


@commands_router.message(CategoryStates.delCategory_state1)
async def category_del(message: Message, state: FSMContext):
    st_date = await state.get_data()
    del_cat_name = st_date.get('del_name')
    await message.answer(text=f"Rostan ham siz '{del_cat_name}' o'chirmoqchimsiz", reply_markup=yes_or_no())
    res = db.del_category(del_cat_name)
    print()
    if res:
        await message.answer(text=f"{del_cat_name} kategoriya o'chrildi")
    else:
        await message.answer(text=f"o'chrishda xatolig yuz berdi")
    await state.clear()


@commands_router.callback_query(CategoryStates.updCategory_state_list)
async def callback_category_edit(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryStates.updCategory_state_new)
    await callback.message.answer(f"Please, send new name for category '{callback.data}'")
    await callback.message.delete()


@commands_router.message(CategoryStates.updCategory_state_new)
async def set_new_category_name(message: Message, state: FSMContext):
    st_data = await state.get_data()
    old_cat = st_data.get('cat_name')
    res = db.upd_category(message.text, old_cat)
    if res['status']:
        await message.answer("Category name successfully changed")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])


@commands_router.message(Command("add_product"))
async def add_product_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.addCategory_state)
    await message.answer(text=f"Qaysi kategoriyaga mahsulot qo'shmoqchisiz", reply_markup=make_category_list())


@commands_router.callback_query(CategoryStates.addCategory_state)
async def callback_category_add(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryStates.addCategory_state_name)
    print(callback.data)
    await callback.message.delete()
    await callback.message.answer(text="Mahsulot nomni krting")

@commands_router.message(CategoryStates.addCategory_state_name)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(pruduct_name=message.text)
    try:
        await state.set_state(CategoryStates.addCategory_state_image)
        await message.answer(text="Mahsulot rasmini yuboring")
    except Exception as e:
        print(e)


@commands_router.message(CategoryStates.addCategory_state_image)
async def add_prodict_image(message: Message, state: FSMContext):
    rasm = message.photo[-1]
    rasm_id = rasm.file_id
    rasm_file = await message.bot.get_file(rasm_id)
    await state.update_data(product_path_image=rasm_file.file_path)
    # await message.bot.download(rasm_file.file_path,
    #                     destination="C:\\Users\\Victus\\Desktop\\python\\6-oy\\online-store-bot\\dow\\" +
    #                     message.document.file_name)
    # rasmni tuklab olish o'xshmadi
    product_info = await state.get_data()
    cat_name = product_info.get("cat_name")
    pruduct_name = product_info.get("pruduct_name")
    product_path_image = product_info.get("product_path_image")
    res = db.add_product_db(pruduct_name, product_path_image, cat_name)
    await state.clear()
    if res:
        await message.answer(text=f"Mahsulot qo'shldi")
    else:
        await message.answer(text="malumo krtishda xatolik yuz berdi iltimos bohsqattan urinib ko'ring")
