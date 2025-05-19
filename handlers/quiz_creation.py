from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database import Option, Question, Quiz, session
from states.quiz import QuizCreationStates

router = Router()


@router.message(Command('create_quiz'))
async def create_quiz(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.chat.id, 'Введи заголовок для опроса')
    await state.set_state(QuizCreationStates.title)


@router.message(QuizCreationStates.title)
async def quiz_title(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.chat.id, 'Введи описание')
    await state.set_state(QuizCreationStates.description)
    await state.set_data({'title': message.text})


@router.message(QuizCreationStates.description)
async def quiz_desc(message: Message, bot: Bot, state: FSMContext):
    quiz = Quiz(author=message.chat.id, title=await state.get_value('title'), description=message.text)
    session.add(quiz)
    session.commit()

    await request_new_question(message.chat.id, quiz.id, bot, state)


@router.message(QuizCreationStates.question)
async def question_state(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.chat.id, 'Введите ответ на вопрос')
    await state.set_state(QuizCreationStates.answer)
    await state.set_data((await state.get_data()) | {'title': message.text})


async def request_new_question(chat_id: int, quiz_id: int, bot: Bot, state: FSMContext):
    await bot.send_message(chat_id, 'Введите вопрос')
    await state.set_state(QuizCreationStates.question)
    await state.set_data((await state.get_data()) | {'quiz_id': quiz_id})


async def request_new_option(chat_id: int, ques_id: int, bot: Bot, state: FSMContext):
    await bot.send_message(chat_id, 'Введите опцию')
    await state.set_state(QuizCreationStates.option)
    await state.set_data((await state.get_data()) | {'ques_id': ques_id})


async def request_action(chat_id: int, quiz_id: int, ques_id: int, bot: Bot, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить опцию', callback_data=f'add_option/{ques_id}')],
        [InlineKeyboardButton(text='Следующий вопрос', callback_data=f'add_ques/{quiz_id}')],
        [InlineKeyboardButton(text='Создать опрос', callback_data=f'creation_done/{quiz_id}')]
    ])
    await bot.send_message(chat_id, 'Выберите действие', reply_markup=markup)
    await state.clear()


@router.callback_query(F.data.split('/')[0] == 'add_ques')
async def quiz_add_question(callback: CallbackQuery, bot: Bot, state: FSMContext):
    quiz_id = int(callback.data.split('/')[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    await request_new_question(callback.from_user.id, quiz_id, bot, state)


@router.message(QuizCreationStates.answer)
async def quiz_answer_state(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    quiz_id = int(data['quiz_id'])

    question = Question(quiz_id=quiz_id, title=data['title'])
    answer = Option(question=question, title=message.text)
    session.add_all([question, answer])
    session.commit()
    question.answer_id = answer.id
    session.commit()

    ques_id = question.id

    await request_action(message.chat.id, quiz_id, ques_id, bot, state)


@router.message(QuizCreationStates.option)
async def quiz_option_state(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    ques_id = int(data['ques_id'])

    option = Option(ques_id=ques_id, title=message.text)
    session.add(option)
    session.commit()

    quiz_id = option.question.quiz_id

    await request_action(message.chat.id, quiz_id, ques_id, bot, state)


@router.callback_query(F.data.split('/')[0] == 'add_option')
async def quiz_add_answer(callback: CallbackQuery, bot: Bot, state: FSMContext):
    ques_id = int(callback.data.split('/')[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    await request_new_option(callback.from_user.id, ques_id, bot, state)


@router.callback_query(F.data.split('/')[0] == 'creation_done')
async def creation_done(callback: CallbackQuery, bot: Bot):
    quiz_id = int(callback.data.split('/')[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(callback.from_user.id, 'Опрос создан!\n\n'
                                                  f'Ссылка: https://t.me/quizzesmakerbot?start={quiz_id}')
