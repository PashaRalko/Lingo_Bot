import random

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

import config
import keyboard
import languages
import database

bot = Bot(token=config.TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Registration(StatesGroup):
    name = State()
    age = State()
    country = State()
    language = State()
    photo = State()


# Обработчик на сообщение "Регистрация" без текущего состояния (state=None)
@dp.message_handler(Text("Регистрация"), state=None)
async def get_name(message: types.Message, state: FSMContext):
    # Получаем первый chat_id из таблицы registration_table
    database.cursor.execute(f"SELECT * FROM registration_table WHERE chat_id = {message.chat.id}")
    result_user = database.cursor.fetchone()
    result_name = result_user[2]
    # Если chat_id из сообщения уже есть в таблице, то выводим информацию о пользователе
    if result_name is not None:
        # Отправляем фото и информацию о пользователе
        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, (message.chat.id,))
        global user_result
        user_result = database.cursor.fetchone()
        await bot.send_photo(message.chat.id, user_result[6],
                             caption=f"У тебя уже есть аккаунт!\n"
                                     f"{languages.languages[user_result[5]]['name']}: {user_result[2]}\n"
                                     f"{languages.languages[user_result[5]]['age']}: {user_result[3]}\n"
                                     f"{languages.languages[user_result[5]]['country']}: {user_result[4]}\n"
                                     f"{languages.languages[user_result[5]]['language']}: {user_result[5]}")
        # Предлагаем пользователю отредактировать информацию
        await message.answer(text=languages.languages[user_result[5]]['edit'], reply_markup=keyboard.inline_edit_kb)
    # Если chat_id из сообщения нет в таблице, то начинаем процесс регистрации
    else:
        # Приветствуем пользователя и запрашиваем его имя
        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, (message.chat.id,))
        user_result = database.cursor.fetchone()
        user_lang = user_result[5]
        await message.answer(languages.languages[user_lang]['hi'],
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer(languages.languages[languages.user_language]['name_input'])
        await Registration.name.set()


# состояние name
@dp.message_handler(state=Registration.name)
async def get_age(message: types.Message, state: FSMContext):
    # Получаем имя пользователя и переходим к следующему состоянию - запрос возраста
    name = message.text
    await state.update_data(name_answer=name)
    await message.answer(languages.languages[user_result[5]]['age_input'])
    await Registration.age.set()


# состояние age
@dp.message_handler(state=Registration.age)
async def get_country(message: types.Message, state: FSMContext):
    # Получаем возраст пользователя и переходим к следующему состоянию - запрос страны
    age = message.text
    try:
        age = int(age)
        await state.update_data(age_answer=age)
        await message.answer(languages.languages[user_result[5]]['country_input'])
        await Registration.country.set()
    except:
        await message.reply(languages.languages[user_result[5]]['not_number'])


# состояние language
@dp.message_handler(state=Registration.country)
async def get_photo(message: types.Message, state: FSMContext):
    country = message.text
    await state.update_data(country_answer=country)
    await message.answer(languages.languages[user_result[5]]['photo_input'])
    await Registration.photo.set()


# Обработка сообщений, которые не являются изображениями в процессе регистрации.
@dp.message_handler(state=Registration.photo)
async def process_wrong_content(message: types.Message):
    await message.reply(languages.languages[user_result[5]]['not_image'])


# Обработчик для сообщений с фотографиями, который сохраняет фото и данные пользователя в базу данных
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Registration.photo)
async def info(message: types.Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()

    # Сохраняем фото на сервере
    file_path = f"user_images\{message.chat.id}_{user_result[2]}.jpg"
    await message.photo[-1].download(file_path)

    # Читаем фото и сохраняем в переменную image_data
    with open(file_path, 'rb') as f:
        image_data = f.read()

    # Получаем ответы пользователя на предыдущие вопросы
    name_answer = data.get('name_answer')
    age_answer = data.get('age_answer')
    country_answer = data.get('country_answer')
    photo = image_data

    query = "SELECT chat_id FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result_id = database.cursor.fetchone()
    if result_id is None:
        # Добавляем данные пользователя в базу данных
        database.cursor.execute(
            "INSERT INTO registration_table (chat_id, name, age, country,photo) VALUES (?, ?, ?, ?, ?)",
            (message.chat.id, name_answer, age_answer, country_answer, photo))
        database.conn.commit()

        # Завершаем состояние

    else:
        update_query = f"UPDATE registration_table SET " \
                       f"name = ?, " \
                       f"age = ?, " \
                       f"country = ?, " \
                       f"photo = ? " \
                       f"WHERE chat_id = ?"
        values = (name_answer, age_answer, country_answer, photo, message.chat.id)
        database.cursor.execute(update_query, values)
        database.conn.commit()

        # Отправляем сообщение о завершении регистрации
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[user_result[5]]['profile'])
    # Получаем фото пользователя из базы данных и отправляем его вместе с остальными данными
    query = "SELECT photo FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result = database.cursor.fetchone()

    photo = result[0]
    await bot.send_photo(message.chat.id, photo,
                         caption=f"{languages.languages[user_result[5]]['name']}: {name_answer}\n"
                                 f"{languages.languages[user_result[5]]['age']}: {age_answer}\n"
                                 f"{languages.languages[user_result[5]]['country']}: {country_answer}\n"
                                 f"{languages.languages[user_result[5]]['language']}: {user_result[5]}",
                         reply_markup=keyboard.main_menu)
    await state.finish()


# Обработчик команды /start, который отправляет клавиатуру выбора языка
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    query = f"SELECT language FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    global lang
    lang = database.cursor.fetchone()
    if lang is None:
        await bot.send_message(chat_id=message.chat.id, text='Choose language',
                               reply_markup=keyboard.inline_language_kb)
        print(message.chat.id)
        database.cursor.execute("INSERT INTO registration_table (chat_id) VALUES (?)", (message.chat.id,))
    else:
        await get_name(message, state=None)


@dp.message_handler(text_contains=['Найти собеседника'])
async def find_users(message: types.Message):
    await next_user(message)


@dp.message_handler(text_contains=["Следующий пользователь"])
async def next_user(message: types.Message):
    query = """ SELECT chat_id FROM registration_table"""
    database.cursor.execute(query)
    all_users = database.cursor.fetchall()
    all_users.remove((message.chat.id,))
    if not all_users:
        await bot.send_message(chat_id=message.chat.id, text='У меня пока нет того, кого я могу тебе предложить!',
                               reply_markup=keyboard.find_users)
    else:
        user = random.choice(all_users)
        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, user)
        global result
        result = database.cursor.fetchone()

        photo = result[6]
        await bot.send_photo(message.chat.id, photo,
                             caption=f"{languages.languages[user_result[5]]['name']}: {result[2]}\n"
                                     f"{languages.languages[user_result[5]]['age']}: {result[3]}\n"
                                     f"{languages.languages[user_result[5]]['country']}: {result[4]}\n"
                                     f"{languages.languages[user_result[5]]['language']}: {result[5]}\n"
                                     f"Выбери следующее действие?", reply_markup=keyboard.find_users)


@dp.message_handler(text_contains=["Общаться с этим пользователем!"])
async def next_user_command(message: types.Message):
    database.cursor.execute(f"SELECT * FROM likes_table WHERE user_1 = {result[1]} AND user_2 = {message.chat.id}")
    user_2_row = database.cursor.fetchone()
    if user_2_row is not None:
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[user_result[5]]['wants_to_chat'],
                               reply_markup=keyboard.find_users)
    else:
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[user_result[5]]['request_sent'],
                               reply_markup=keyboard.find_users)
        database.cursor.execute("INSERT INTO likes_table (user_1, user_2, like) VALUES (?, ?, ?)",
                                (message.chat.id, result[1], 0))

        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, (message.chat.id,))
        res = database.cursor.fetchone()
        await bot.send_photo(result[1], res[6],
                             caption=f"{languages.languages[user_result[5]]['name']}: {res[2]}\n"
                                     f"{languages.languages[user_result[5]]['age']}: {res[3]}\n"
                                     f"{languages.languages[user_result[5]]['country']}: {res[4]}\n"
                                     f"{languages.languages[user_result[5]]['language']}: {res[5]}\n"
                                     f"{languages.languages[user_result[5]]['next_step']}",
                             reply_markup=keyboard.find_users)
    database.conn.commit()


@dp.message_handler(text_contains=["Главное меню"])
async def menu(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=languages.languages[user_result[5]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)


@dp.callback_query_handler(text_contains="not_edit")
async def not_edit_profile_btn(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id, text=languages.languages[user_result[5]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


# Определяем обработчик callback_query с текстом, содержащим "edit" и состоянием None
@dp.callback_query_handler(text_contains="edit", state=None)
async def edit_profile_btn(callback: types.CallbackQuery, state: FSMContext):
    # Отправляем пользователю сообщение с просьбой ввести имя
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[user_result[5]]['name_input'])
    # Устанавливаем состояние FSM на "name"
    await Registration.name.set()


# Обработчик нажатий на кнопки с выбором языка
@dp.callback_query_handler(text_contains="english")
async def eng_lang(callback: types.CallbackQuery):
    # Устанавливаем язык пользователя в атрибут объекта languages
    languages.user_language = 'English'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    # Удаляем сообщение с выбором языка
    await callback.message.delete()


# Аналогичные обработчики для других языков
@dp.callback_query_handler(text_contains="french")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'French'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="deutsch")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'Deutsch'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="сhinese")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'Chinese'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="italiano")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'Italiano'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="russian")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'Русский'
    database.cursor.execute(
        f"UPDATE registration_table SET language = '{languages.user_language}' WHERE chat_id = {callback.from_user.id}")
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


# Запуск бота
if __name__ == '__main__':
    print("Bot is running")
    executor.start_polling(dp, skip_updates=True)
