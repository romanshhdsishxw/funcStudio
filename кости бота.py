import asyncio
import os
import psycopg2

from psycopg2 import sql
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv


def insert_record_users(name, univer, direction, biography) -> None:
    print('asdsdas')
    try:
        # Установление соединения с базой данных
        connection = psycopg2.connect(
            dbname='teacher',
            user='postgres',
            password='WfhtyjdHjvfy2007!!!',
            host='localhost',
            port='5432'
        )

        cursor = connection.cursor()

        # Использование параметризованного запроса для предотвращения SQL-инъекций
        insert_query = sql.SQL("""
            INSERT INTO users (name, univer, direction, biography)
            VALUES (%s, %s, %s, %s)
        """)

        # Выполнение запроса
        cursor.execute(insert_query, (name, univer, direction, biography))

        # Подтверждение изменений
        connection.commit()

        print("Запись успешно добавлена в таблицу")

    except Exception as error:
        print(f"Произошла ошибка: {error}")

    # finally:
    #     if cursor:
    #         cursor.close()
    #     if connection:
    #         connection.close()


def insert_record_teachers(name, univer, direction, biography) -> None:
    print('asdsdas')
    try:
        # Установление соединения с базой данных
        connection = psycopg2.connect(
            dbname='teacher',
            user='postgres',
            password='WfhtyjdHjvfy2007!!!',
            host='localhost',
            port='5432'
        )

        cursor = connection.cursor()

        # Использование параметризованного запроса для предотвращения SQL-инъекций
        insert_query = sql.SQL("""
            INSERT INTO teacher (name, univer, direction, biography)
            VALUES (%s, %s, %s, %s)
        """)

        # Выполнение запроса
        cursor.execute(insert_query, (name, univer, direction, biography))

        # Подтверждение изменений
        connection.commit()

        print("Запись успешно добавлена в таблицу")

    except Exception as error:
        print(f"Произошла ошибка: {error}")

    # finally:
    #     if cursor:
    #         cursor.close()
    #     if connection:
    #         connection.close()


class User(StatesGroup):
    username = State()
    user_type = State()
    user_subject = State()
    user_id = State()
    user_UNI = State()


async def command_start(message: Message) -> None:
    tab = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Найти репетитора')
        ]

    ])
    await message.answer("Привет!")


async def registrate(message: Message, state: FSMContext) -> None:
    """
    Запускает процесс регистрации пользователя.
    """
    await state.set_state(User.username)  # Устанавливаем состояние для ввода имени
    await message.answer("Пожалуйста, введите ваше имя:")  # Запрашиваем имя


async def taking_type(message: Message, state: FSMContext) -> None:
    """
    Получает имя пользователя и предлагает выбрать тип пользователя (учитель/ученик).
    """
    # Получаем имя из предыдущего состояния и сохраняем его
    await state.update_data(username=message.text)
    await state.set_state(User.user_type)  # Переходим к состоянию выбора типа пользователя

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(text="Учитель"),
            KeyboardButton(text="Ученик")
        ],
    ])

    data = await state.get_data()  # Получаем данные из состояния
    name = data['username']  # Получаем имя пользователя
    await message.answer(f'{name}, вы учитель или ученик?', reply_markup=kb)


async def taking_subject(message: Message, state: FSMContext) -> None:
    """
    Получает тип пользователя (учитель/ученик) и, если это учитель, запрашивает список предметов.
    """
    user_type = message.text
    await state.update_data(user_type=user_type)  # Сохраняем тип пользователя

    if user_type == "Ученик":
        await state.set_state(User.user_subject)
        await message.answer('''Напиши список предметов, которые тебя интересуют, через запятую и без пробелов.
Пример: "математика,русский,физика" ''')
    elif user_type == "Учитель":
        await state.set_state(User.user_subject)
        await message.answer('''Пожалуйста, напишите, какой предмет вы преподаете''')
    else:
        await message.answer("Пожалуйста, выберите 'Учитель' или 'Ученик' используя кнопки.")


async def taking_id(message: Message, state: FSMContext) -> None:
    await state.update_data(user_subject=message.text)  # Сохраняем предметы (если это учитель)
    await state.set_state(User.user_id)
    await message.answer('Пожалуйста, напишите свой тг-логин, чтобы с вами можно было связаться')


async def registrate_end(message: Message, state: FSMContext) -> None:
    await state.update_data(user_id=message.text)
    data = await state.get_data()
    username = data.get('username', 'Не указано')
    user_type = data.get('user_type', 'Не указано')
    user_subject = data.get('user_subject', 'Не указано')
    user_id = data.get('user_id', 'Не указано')
    # Формируем сообщение с данными пользователя
    message_text = f"Регистрация прошла успешно!\n\n" \
                   f"Имя: {username}\n" \
                   f"Тип: {user_type}\n" \
                   f"Предметы: {user_subject}\n" \
                   f"Telegram ID: {user_id}"
    await message.answer(message_text)  # нужно вставить сюда данные пользователя в формате таблицы с пунктами
    await state.clear()  # Очищаем состояние после регистрации

    if user_type == "Студент":
        insert_record_users(name=username, univer=None, direction=user_subject, biography=None)
    if user_type == "Учитель":
        insert_record_teachers(name=username, univer=None, direction=user_subject, biography=None)


async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    dp = Dispatcher()
    dp.message.register(command_start, Command("start"))
    dp.message.register(registrate, Command("registrate"))
    dp.message.register(taking_type, User.username)  # Регистрируем taking_type для обработки имени
    dp.message.register(taking_subject, User.user_type)  # Регистрируем taking_subject для обработки выбора типа
    dp.message.register(taking_id, User.user_subject)  # Регистрируем taking_id для обработки предметов
    dp.message.register(registrate_end, User.user_id)  # Регистрируем registrate_end для завершения регистрации

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
