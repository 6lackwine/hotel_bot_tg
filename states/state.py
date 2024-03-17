from telebot.handler_backends import State, StatesGroup

class MyStates(StatesGroup):
    s_start = State()
    s_city = State()
    s_date_from = State()
    s_date_to = State()
    s_count_human = State()
    s_result = State()

class LowStates(StatesGroup):
    s_start = State()
    s_city = State()
    s_date_from = State()
    s_date_to = State()
    s_count_human = State()

class HighStates(StatesGroup):
    s_start = State()
    s_city = State()
    s_date_from = State()
    s_date_to = State()
    s_count_human = State()

