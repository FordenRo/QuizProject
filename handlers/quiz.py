from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from database import Option, Question, Quiz, session, UserAnswer

router = Router()


async def open_quiz(chat_id: int, quiz_id: int, bot: Bot):
    quiz = session.scalar(select(Quiz).where(Quiz.id == quiz_id))
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Начать прохождение', callback_data=f'start/{quiz.id}')]])
    await bot.send_message(chat_id,
                           f'<b>{quiz.title}</b>\n{quiz.description}\n\n<i>Опрос включает <b>{len(quiz.questions)}</b> вопросов</i>',
                           reply_markup=markup, parse_mode='HTML')


@router.callback_query(F.data.split('/')[0] == 'start')
async def start_quiz(callback: CallbackQuery, bot: Bot):
    quiz_id = int(callback.data.split('/')[1])
    quiz = session.scalar(select(Quiz).where(Quiz.id == quiz_id))
    question = quiz.questions[0]
    await send_question(callback.from_user.id, quiz, question, bot)


async def send_question(chat_id: int, quiz: Quiz, ques: Question, bot: Bot, message_to_edit: Message | None = None):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=option.title, callback_data=f'ans/{option.id}')]
                         for option in ques.options]
    )
    text = f'Вопрос #{quiz.questions.index(ques) + 1}/{len(quiz.questions)}\n{ques.title}'

    if message_to_edit:
        await message_to_edit.edit_text(text, reply_markup=markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=markup)


async def finish_quiz(message: Message, quiz: Quiz, bot: Bot):
    user_answers = session.scalars(select(UserAnswer).where(UserAnswer.quiz == quiz,
                                                            UserAnswer.user_id == message.chat.id)).all()
    rights = list(filter(lambda user_answer: user_answer.option_id == user_answer.question.answer_id, user_answers))
    await message.edit_text(f'Викторина пройдена!\n\nВы правильно ответили на {len(rights)} вопросов')


@router.callback_query(F.data.split('/')[0] == 'ans')
async def answer_question(callback: CallbackQuery, bot: Bot):
    option_id = int(callback.data.split('/')[1])
    option: Option = session.scalar(select(Option).where(Option.id == option_id))
    question = option.question
    quiz = question.quiz
    next_index = quiz.questions.index(question) + 1

    user_answer = UserAnswer(user_id=callback.from_user.id, quiz=quiz, question=question, option_id=option_id)
    session.add(user_answer)
    session.commit()

    if next_index < len(quiz.questions):
        next_question = quiz.questions[next_index]

        await send_question(callback.from_user.id, quiz, next_question, bot, callback.message)
    else:
        await finish_quiz(callback.message, quiz, bot)

    await callback.answer()
