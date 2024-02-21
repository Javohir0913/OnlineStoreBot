from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    newCategory_state = State()

    updCategory_state_list = State()
    updCategory_state_new = State()

    delCategory_state = State()
    delCategory_state1 = State()

    del_cat_state = State()


    addCategory_state = State()
    addCategory_state_name = State()
    addCategory_state_image = State()