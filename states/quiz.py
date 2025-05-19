from aiogram.fsm.state import State, StatesGroup


class QuizCreationStates(StatesGroup):
    title = State()
    description = State()
    question = State()
    answer = State()
    option = State()
