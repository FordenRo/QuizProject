from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database import Quiz, session, Question, Option, UserAnswer

router = Router()


@router.callback_query(F.data.split('/')[0] == 'res')
async def send_result(callback: CallbackQuery):
    ques_id = callback.data.split('/')[1]
    question = session.scalar(select(Question).where(Question.id == ques_id))
    quiz = question.quiz
    ques_idx = quiz.questions.index(question)
    answer = session.scalar(select(Option).where(Option.id == question.answer_id))
    user_answer_option_id = session.scalar(select(UserAnswer).where(UserAnswer.user_id == callback.from_user.id,
                                                                    UserAnswer.question == question)).option_id
    user_answer = session.scalar(select(Option).where(Option.id == user_answer_option_id))

    text = (f'Вопрос #{quiz.questions.index(question) + 1}/{len(quiz.questions)}\n'
            f'{question.title}\n\n'
            f'Ваш ответ: {user_answer.title}\n'
            f'Правильный ответ: {answer.title}\n\n'
            f'Вы ответили {'правильно!' if answer.id == user_answer_option_id else 'неправильно.'}')
    buttons = []

    if ques_idx > 0:
        prev = quiz.questions[ques_idx - 1]
        buttons += [InlineKeyboardButton(text='Назад', callback_data=f'res/{prev.id}')]

    if ques_idx + 1 < len(quiz.questions):
        next = quiz.questions[ques_idx + 1]
        buttons += [InlineKeyboardButton(text='Дальше', callback_data=f'res/{next.id}')]

    exit_button = InlineKeyboardButton(text='Выход', callback_data='exit')
    markup = InlineKeyboardMarkup(inline_keyboard=[buttons] + [[exit_button]])
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == 'exit')
async def ex(callback: CallbackQuery):
    await callback.message.delete()
