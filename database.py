from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    answer_id: Mapped[int] = mapped_column(nullable=True)
    options: Mapped[list['Option']] = relationship(back_populates='question')
    user_answers: Mapped[list['UserAnswer']] = relationship(back_populates='question')

    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'))
    quiz: Mapped['Quiz'] = relationship(back_populates='questions')


class Option(Base):
    __tablename__ = 'options'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()

    ques_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    question: Mapped['Question'] = relationship(back_populates='options')


class UserAnswer(Base):
    __tablename__ = 'user_answers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()

    option_id: Mapped[int] = mapped_column()

    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    question: Mapped['Question'] = relationship(back_populates='user_answers')

    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'))
    quiz: Mapped['Quiz'] = relationship(back_populates='user_answers')


class Quiz(Base):
    __tablename__ = 'quizzes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    author: Mapped[int] = mapped_column()

    user_answers: Mapped[list['UserAnswer']] = relationship(back_populates='quiz')
    questions: Mapped[list['Question']] = relationship(back_populates='quiz')


engine = create_engine('sqlite:///:memory:')
session = Session(engine)
