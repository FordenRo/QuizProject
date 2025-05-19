from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from database import session, UserAnswer
from handlers.quiz import open_quiz

router = Router()


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    args = message.text.split()
    if len(args) > 1:
        quiz_id = int(args[1])
        if session.scalar(select(UserAnswer).where(UserAnswer.user_id == message.chat.id,
                                                   UserAnswer.quiz_id == quiz_id)):
            await bot.send_message(message.chat.id, 'Вы уже прошли данную викторину!')
        else:
            await open_quiz(message.chat.id, quiz_id, bot)
    else:
        await bot.send_message(message.chat.id, 'Привет!')
    await message.delete()
