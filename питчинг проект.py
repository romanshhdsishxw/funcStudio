import asyncio
import os
import time

import psycopg2
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from psycopg2 import sql


def get_records_by_direction(direction):
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
        select_query = sql.SQL("""
            SELECT id, biography FROM teacher WHERE direction = %s
        """)

        # Выполнение запроса
        cursor.execute(select_query, (direction,))

        # Извлечение всех записей
        records = cursor.fetchall()

        # Обработка и вывод результатов
        if records:
            for record in records:
                print(f"ID: {record[0]}, Biography: {record[1]}")
        else:
            print("Нет записей, соответствующих указанному направлению.")

    except Exception as error:
        print(f"Произошла ошибка: {error}")

    # finally:
    #     if cursor:
    #         cursor.close()
    #     if connection:
    #         connection.close()


def insert_record_users(name, univer, direction, biography) -> None:
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
    tutor_request = State()


async def command_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start. Предлагает выбор: Регистрация или найти репетитора.
    """
    tab = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Найти репетитора')
        ]
    ])

    await message.answer("Привет! Что вы хотите сделать?", reply_markup=tab)
    await state.set_state(None)  # Сбрасываем состояние FSM


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
    await state.update_data(username=message.text)
    await state.set_state(User.user_type)

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(text="Преподаватель"),
            KeyboardButton(text="Студент")
        ],
    ])
    data = await state.get_data()  # Получаем данные из состояния
    name = data['username']
    await message.answer(f'{name}, ты преподаватель или студент?', reply_markup=kb)


async def taking_subject(message: Message, state: FSMContext) -> None:
    """
    Получает тип пользователя (учитель/ученик) и, если это ученик, запрашивает список предметов.
    """
    user_type = message.text
    await state.update_data(user_type=user_type)  # Сохраняем тип пользователя

    if user_type == "Студент":
        await state.set_state(User.user_subject)
        await message.answer('''Напиши список предметов, которые тебя интересуют, через запятую и без пробелов.
Пример: "математика,русский,физика" ''')
    elif user_type == "Преподаватель":
        await state.set_state(User.user_subject)
        await message.answer('''Пожалуйста, напишите, какой предмет вы преподаете''')
    else:
        await message.answer("Пожалуйста, выберите 'Преподаватель' или 'Студент' используя кнопки.")


async def taking_id(message: Message, state: FSMContext) -> None:
    await state.update_data(user_subject=message.text)  # Сохраняем предметы (или предмет учителя)
    await state.set_state(User.user_id)
    await message.answer('Пожалуйста, напишите свой тг-логин, чтобы с вами можно было связаться (без @)')


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
                   f"Предметы/Предмет: {user_subject}\n" \
                   f"Telegram ID: @{user_id}"
    await message.answer(message_text)  # Нужно вставить сюда данные пользователя в формате таблицы с пунктами
    await state.clear()  # Очищаем состояние после регистрации
    await command_start(message, state)  # Возвращаемся к стартовому меню

    if user_type == "Преподаватель":
        insert_record_teachers(name=username, univer=None, direction=user_subject, biography=None)
    if user_type == "Студент":
        insert_record_users(name=username, univer=None, direction=user_subject, biography=None)


async def find_tutor(message: Message, state: FSMContext) -> None:
    """
    Обработчик для кнопки "Найти репетитора".
    Запрашивает описание нужного преподавателя и отправляет запрос в YandexGPT.
    """
    await state.set_state(User.tutor_request)
    await message.answer('''Пожалуйста, опишите преподавателя, который вам нужен.
Возраст, пол, темперамент, стаж работы.
Я подберу вам подходящий вариант, основываясь на ваших пожеланиях''')


async def process_tutor_request(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает запрос пользователя на подбор репетитора, используя YandexGPT.
    """
    await state.update_data(tutor_request=message.text)
    await message.answer("Пожалуйста, подождите, я ищу подходящего репетитора...")

    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'

    system_prompt = '''Напиши возможное резюме на данный запрос'''
    user_prompt = message.text

    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': 2000},
        'messages': [
            {'role': 'system', 'text': system_prompt},
            {'role': 'user', 'text': user_prompt},
        ],
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {api_key}'
    }

    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json().get('id')

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(1)

    data = response.json()
    answer = data['response']['alternatives'][0]['message']['text']

    await message.answer(answer)


async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    dp = Dispatcher()

    # Регистрируем обработчики команд
    dp.message.register(command_start, Command("start"))

    # Регистрируем обработчики кнопок с использованием F.text.in
    dp.message.register(registrate, F.text == "Регистрация")
    dp.message.register(find_tutor, F.text == "Найти репетитора")

    # Регистрируем обработчики FSM
    dp.message.register(taking_type, User.username)
    dp.message.register(taking_subject, User.user_type)
    dp.message.register(taking_id, User.user_subject)
    dp.message.register(registrate_end, User.user_id)

    # Регистрируем обработчик запроса репетитора
    dp.message.register(process_tutor_request, User.tutor_request)

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
