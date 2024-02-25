from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.client_inline_keyboards import show_ads_l_r, msg_shou
from states.client_states import MsgAllAds
from config import DB_NAME
from utils.database import Database

msg_router = Router()
db = Database(DB_NAME)


@msg_router.message()
async def msg_handler(message: Message, state: FSMContext):
    balans = 0
    if message.text.lower() in ["macbook", "makbook", "macbuk", "makbuk", "макбук"]:
        all_ads = db.search("macbook")
        if len(all_ads) < 11:
            x = f'Ad 1-{len(all_ads)} from {len(all_ads)}:\n\n'
            for son, ad in enumerate(all_ads):
                x += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
            await message.answer(text=x, reply_markup=msg_shou(len(all_ads), all_ads))
            await state.set_state(MsgAllAds.msgAds)
        else:
            kb_ads_list = []
            for i in range(0, len(all_ads), 10):
                kb_ads_list.append(all_ads[i: i + 10])
            if len(all_ads) % 10 != 0:
                kb_ads_list.append(all_ads[(len(all_ads) // 10) * 10:])
                balans = 1
            x = f'Ad 1-10 from {len(all_ads)}:\n\n'
            for son, ad in enumerate(all_ads[:10]):
                x += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
            await message.answer(text=x, reply_markup=show_ads_l_r(10, all_ads[:10]))
            await state.update_data(kb_ads_list=kb_ads_list)
            await state.update_data(ads_max=len(all_ads))
            await state.update_data(index=0)
            await state.update_data(balans=balans)
            await state.set_state(MsgAllAds.msgAds)

    elif message.text.lower() in ["hp", "lenovo"]:
        all_ads = db.search(message.text)
        if len(all_ads) < 11:
            x = f'Ad 1-{len(all_ads)} from {len(all_ads)}:\n\n'
            for son, ad in enumerate(all_ads):
                x += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
            await message.answer(text=x, reply_markup=msg_shou(len(all_ads), all_ads))
            await state.set_state(MsgAllAds.msgAds)

        else:
            kb_ads_list = []
            for i in range(0, len(all_ads), 10):
                kb_ads_list.append(all_ads[i: i + 10])
            if len(all_ads) % 10 != 0:
                kb_ads_list.append(all_ads[(len(all_ads) // 10) * 10:])
                balans = 1
            x = f'Ad 1-10 from {len(all_ads)}:\n\n'
            for son, ad in enumerate(all_ads[:10]):
                x += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
            await message.answer(text=x, reply_markup=show_ads_l_r(10, all_ads[:10]))
            await state.update_data(kb_ads_list=kb_ads_list)
            await state.update_data(ads_max=len(all_ads))
            await state.update_data(index=0)
            await state.update_data(balans=balans)
            await state.set_state(MsgAllAds.msgAds)

    else:
        await message.answer(text=f"'{message.text}' bunday elonlar mavjud emas")


@msg_router.callback_query(MsgAllAds.msgAds)
async def call_msg(callback: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    kb_ads_list = all_data.get("kb_ads_list")
    index = all_data.get("index")
    ads_max = all_data.get("ads_max")
    balans = all_data.get("balans")
    if callback.data.isdigit():
        ads = db.get_ads(callback.data)
        await callback.message.answer_photo(
            photo=ads[4],
            caption=f"<b>{ads[1]}</b>\n\n"
                    f"{ads[2]}\n\nPrice: ${ads[3]}",
            parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == "cancel":
        await callback.message.delete()
        await state.clear()
    elif callback.data == "right":
        if len(kb_ads_list) - (1+balans) == index:
            index = 0
        else:
            index += 1
        await state.update_data(index=index)
        text = f"Ad {index * 10 + 1}-{ads_max if len(kb_ads_list) - (1+balans) == index else index * 10 + 10} from {ads_max}:\n\n"
        for son, ad in enumerate(kb_ads_list[index]):
            text += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
        await callback.message.edit_text(text=text,
                                         reply_markup=show_ads_l_r(len(kb_ads_list[index]), kb_ads_list[index]))
    else:
        if index == 0:
            index = len(kb_ads_list) - (1+balans)
        else:
            index -= 1
        await state.update_data(index=index)
        text = f"Ad {index * 10 + 1}-{ads_max if len(kb_ads_list) - (1+balans) == index else index * 10 + 10} from {ads_max}:\n\n"
        for son, ad in enumerate(kb_ads_list[index]):
            text += f"{son + 1}. {ad[1]}:    Price: {ad[3]}\n"
        await callback.message.edit_text(text=text,
                                         reply_markup=show_ads_l_r(len(kb_ads_list[index]), kb_ads_list[index]))
