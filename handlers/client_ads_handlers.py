from time import time

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.client_inline_keyboards import get_category_list, get_product_list, ads_list, yes_or_no, edit_ads, sahifa
from states.client_states import ClientAdsStates, ClientDelAdsStates, ClientEditStates, AdsStates
from utils.database import Database
from utils.my_commands import commands_user

ads_router = Router()
db = Database(DB_NAME)

#
# @ads_router.message(F.photo)
# async def test(message: Message, album: list(Message)):
#     print(album)


@ads_router.message(Command('new_ad'))
async def new_ad_handler(message: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdCategory)
    await message.answer(
        "Please, choose a category for your ad: ",
        reply_markup=get_category_list()
    )


@ads_router.callback_query(ClientAdsStates.selectAdCategory)
async def select_ad_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdProduct)
    await callback.message.edit_text(
        "Please, choose a product type for your ad: ",
        reply_markup=get_product_list(int(callback.data))
    )


@ads_router.callback_query(ClientAdsStates.selectAdProduct)
async def select_ad_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.insertTitle)
    await state.update_data(ad_product=callback.data)
    await callback.message.answer(
        f"Please, send title for your ad!\n\n"
        f"For example:"
        f"\n\t- iPhone 15 Pro Max 8/256 is on sale"
        f"\n\t- Macbook Pro 13\" M1 8/256 is on sale"
    )
    await callback.message.delete()


@ads_router.message(ClientAdsStates.insertTitle)
async def ad_title_handler(message: Message, state: FSMContext):
    await state.update_data(ad_title=message.text)
    await state.set_state(ClientAdsStates.insertText)
    await message.answer("OK, please, send text(full description) for your ad.")


@ads_router.message(ClientAdsStates.insertText)
async def ad_text_handler(message: Message, state: FSMContext):
    await state.update_data(ad_text=message.text)
    await state.set_state(ClientAdsStates.insertPrice)
    await message.answer("OK, please, send price for your ad (only digits).")


@ads_router.message(ClientAdsStates.insertPrice)
async def ad_price_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(ad_price=int(message.text))
        await state.set_state(ClientAdsStates.insertImages)
        await message.answer("OK, please, send image(s) for your ad.")
    else:
        await message.answer("Please, send only number...")


@ads_router.message(ClientAdsStates.insertImages)
async def ad_photo_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(ad_photo=message.photo[-1].file_id)
        await state.set_state(ClientAdsStates.insertPhone)
        await message.answer("OK, please, send phone number for contact with your.")
    else:
        await message.answer("Please, send image(s)...")


@ads_router.message(ClientAdsStates.insertPhone)
async def ad_phone_handler(message: Message, state: FSMContext):
    await state.update_data(ad_phone=message.text)
    all_data = await state.get_data()
    try:
        x = db.insert_ad(
            title=all_data.get('ad_title'),
            text=all_data.get('ad_text'),
            price=all_data.get('ad_price'),
            image=all_data.get('ad_photo'),
            phone=all_data.get('ad_phone'),
            u_id=message.from_user.id,
            prod_id=all_data.get('ad_product'),
            date=time()
        )
        if x:
            await state.clear()
            await message.answer("Your ad successfully added!")
        else:
            await message.answer("Something error, please, try again later...")
    except:
        await message.answer("Resend phone please...")


@ads_router.message(Command('ads'))
async def ads_list_handler(message: Message, state: FSMContext):
    await state.clear()
    if db.elon_bormi(message.from_user.id)[0] != 0:
        my_ads = db.get_my_ads(message.from_user.id)
        my_ads_list = []
        await state.update_data(count=1)
        await state.update_data(user_id=message.from_user.id)
        for ad in my_ads:
            my_ads_list.append(ad)
        await message.answer_photo(photo=my_ads_list[0][4],
                                   caption=f"<b> {my_ads_list[0][1]}</b>\n\n{my_ads_list[0][2]}\n\nPrice: ${my_ads_list[0][3]}",
                                   parse_mode=ParseMode.HTML, reply_markup=sahifa())
        await state.set_state(AdsStates.clientAds)
    else:
        await message.answer(text="sizda elonlar mavjud emas")


@ads_router.callback_query(AdsStates.clientAds)
async def ads_handler(callback: CallbackQuery, state: FSMContext):
    all_date = await state.get_data()
    user_id = all_date.get("user_id")
    zxc = all_date.get("count")
    my_ads = db.get_my_ads(user_id)
    my_ads_list = []
    for ad in my_ads:
        my_ads_list.append(ad)
    if callback.data != "-1" and zxc >= 0:
        await state.update_data(count=zxc + int(callback.data))
        await callback.message.answer_photo(photo=my_ads_list[zxc][4],
                                   caption=f"<b> {my_ads_list[zxc][1]}</b>\n\n{my_ads_list[zxc][2]}\n\nPrice: ${my_ads_list[zxc][3]}",
                                   parse_mode=ParseMode.HTML, reply_markup=sahifa())
    elif zxc > 0 and callback.data == "-1":
        await state.update_data(count=zxc + int(callback.data))
        await callback.message.answer_photo(photo=my_ads_list[zxc][4],
                                            caption=f"<b> {my_ads_list[zxc][1]}</b>\n\n{my_ads_list[zxc][2]}\n\nPrice: ${my_ads_list[zxc][3]}",
                                            parse_mode=ParseMode.HTML, reply_markup=sahifa())
    else:
        print("zxc")
    print(zxc)


@ads_router.message(Command("del_ad"))
async def start_del_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Qaysi eloni o'chirmoqchisz", reply_markup=ads_list(message.from_user.id))
    await state.set_state(ClientDelAdsStates.delState)


@ads_router.callback_query(ClientDelAdsStates.delState)
async def del_yes_or_no_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(del_ads_name=callback.data)
    await state.set_state(ClientDelAdsStates.delState1)
    await callback.message.edit_text(text=f"' {callback.data} ' elonini rostan ham o'chirmoqchimisiz",
                                     reply_markup=yes_or_no())


@ads_router.callback_query(ClientDelAdsStates.delState1)
async def del_ads_handler(callback: CallbackQuery, state: FSMContext):
    all_date = await state.get_data()
    if callback.data == "yes":
        x = db.del_ads(all_date.get("del_ads_name"))
        if x:
            await callback.message.answer(text=f"{all_date.get("del_ads_name")} muvaffaqitatli o'chrildi")
        else:
            await callback.message.answer(text=f"{all_date.get("del_ads_name")}ni o'chrish muvaffaqitatsiz ")

    else:
        await callback.message.answer(text=f"{all_date.get("del_ads_name")} eloni o'chrish bekor qlindi")
    await callback.message.delete()
    await state.clear()


@ads_router.message(Command("edit_ad"))
async def edit_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Qaysi eloni o'zgartirmoqchisiz", reply_markup=ads_list(message.from_user.id))
    await state.set_state(ClientEditStates.chooseEdit)


@ads_router.callback_query(ClientEditStates.chooseEdit)
async def choose_edit_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(adsname=callback.data)
    await state.set_state(ClientEditStates.chooseEdit1)
    await callback.message.edit_text(text=f"' {callback.data} ' elonigizni shu bo'imlarni o'zgartra olasiz", reply_markup=edit_ads())


@ads_router.callback_query(ClientEditStates.chooseEdit1)
async def choose_edit_handler1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(chooseEdit=callback.data)
    await state.set_state(ClientEditStates.endEdit)
    if callback.data == "price":
        await callback.message.answer(text=f"{callback.data}ni o'zgartirmoqchisz faqat son krting")
    elif callback.data == "image":
        await callback.message.answer(text=f"{callback.data}ni o'zgartirmoqchisz rasm jo'nating")
    else:
        await callback.message.answer(text=f"{callback.data}ni o'zgartirmoqchisz")
    await callback.message.delete()


@ads_router.message(ClientEditStates.endEdit)
async def end_edit(message: Message, state: FSMContext):
    all_date = await state.get_data()
    choose_edit = all_date.get("chooseEdit")
    if choose_edit == "title":
        x = db.edit_title(new_title=message.text, u_id=message.from_user.id)
        if x:
            await message.answer(text="muvaffaqitatli o'zgartrildi /ads bosib ozgarshni ko'rishigiz mumkin")
        else:
            await message.answer(text="o'zgartrish muvaffaqitatsiz bo'ldi")
    elif choose_edit == "text":
        x = db.edit_text(new_text=message.text, u_id=message.from_user.id)
        if x:
            await message.answer(text="muvaffaqitatli o'zgartrildi /ads bosib ozgarshni ko'rishigiz mumkin")
        else:
            await message.answer(text="o'zgartrish muvaffaqitatsiz bo'ldi")
    elif choose_edit == "price" and message.text.isdigit():
        x = db.edit_price(new_price=message.text, u_id=message.from_user.id)
        if x:
            await message.answer(text="muvaffaqitatli o'zgartrildi /ads bosib ozgarshni ko'rishigiz mumkin")
        else:
            await message.answer(text="o'zgartrish muvaffaqitatsiz bo'ldi")
    elif choose_edit == "image":
        x = db.edit_images(new_images=message.photo[-1].file_id, u_id=message.from_user.id)
        if x:
            await message.answer(text="muvaffaqitatli o'zgartrildi /ads bosib ozgarshni ko'rishigiz mumkin")
        else:
            await message.answer(text="o'zgartrish muvaffaqitatsiz bo'ldi")
    else:
        await message.answer(text="o'zgartrish muvaffaqitatsiz bo'ldi")
