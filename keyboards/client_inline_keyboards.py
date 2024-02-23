from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def get_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=category[1],
                callback_data=str(category[0])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories


# Function for make inline keyboards from product names
def get_product_list(cat_id: int) -> InlineKeyboardMarkup:
    products = db.get_products(cat_id)
    rows = []
    for product in products:
        rows.append([
            InlineKeyboardButton(
                text=product[1],
                callback_data=str(product[0])
            )
        ])
    kb_products = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_products


def ads_list(u_id) -> InlineKeyboardMarkup:
    ads = db.get_my_ads(u_id=u_id)
    rows = []
    for ad in ads:
        rows.append([InlineKeyboardButton(text=ad[1],callback_data=str(ad[1]))])

    kb_ads = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_ads


def yes_or_no() -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(text="YES", callback_data="yes"),
        InlineKeyboardButton(text="NO", callback_data="no")
    ]
    rows = [row]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def edit_ads() -> InlineKeyboardMarkup:
    row = [InlineKeyboardButton(text="title", callback_data="title")]
    row1 =[InlineKeyboardButton(text="text", callback_data="text")]
    row2 =[InlineKeyboardButton(text="price", callback_data="price")]
    row3 =[InlineKeyboardButton(text="image", callback_data="image")]
    rows = [row, row1, row2, row3]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def sahifa() -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(text="⬅️", callback_data="-1"),
        InlineKeyboardButton(text="➡️", callback_data="1")
    ]
    row1 = [InlineKeyboardButton(text="Cancel", callback_data="cancel")]
    rows = [row, row1]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
