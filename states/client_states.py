from aiogram.fsm.state import State, StatesGroup


class ClientAdsStates(StatesGroup):
    selectAdCategory = State()
    selectAdProduct = State()
    insertTitle = State()
    insertText = State()
    insertPrice = State()
    insertImages = State()
    insertPhone = State()


class ClientDelAdsStates(StatesGroup):
    delState = State()
    delState1 = State()


class ClientEditStates(StatesGroup):
    chooseEdit = State()
    chooseEdit1 = State()
    endEdit = State()


class AdsStates(StatesGroup):
    clientAds = State()