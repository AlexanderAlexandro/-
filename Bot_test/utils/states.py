from aiogram.fsm.state import State, StatesGroup


class TemplateBuilderState(StatesGroup):
    awaiting_answer = State()


class CalculatorState(StatesGroup):
    awaiting_answer = State()


class AdminBroadcastState(StatesGroup):
    awaiting_text = State()
