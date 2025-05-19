from asyncio import run

from aiogram import Bot, Dispatcher

from database import Base, engine
from handlers import quiz_creation, quiz, start

TOKEN = '7741086976:AAFpPtgxGbHLp6KZRX_MQ_H9JQ8bZEQOifw'


async def main():
    Base.metadata.create_all(engine)

    bot = Bot(TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_routers(start.router,
                               quiz_creation.router,
                               quiz.router)

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    run(main())
