from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database

db = Database(DB_NAME)


# Function for make inline keyboards from category names
def make_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=str(category[1]),
                callback_data=str(category[1])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories


def yes_or_no() -> InlineKeyboardMarkup:
    yn = ['yes', "no"]
    row = [
        InlineKeyboardButton(text="YES", callback_data=yn[0]),
        InlineKeyboardButton(text="NO", callback_data=yn[1])
    ]
    rows = [row]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
