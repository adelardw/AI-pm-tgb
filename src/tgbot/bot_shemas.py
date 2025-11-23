from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    user_confidence = State()
    chat = State()
    main_menu = State()
