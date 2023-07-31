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
@dp.message_handler(Text("Registration"), state=None)
async def get_name(message: types.Message, state: FSMContext):
    # Получаем первый chat_id из таблицы registration_table
    database.cursor.execute(f"SELECT * FROM registration_table WHERE chat_id = {message.chat.id}")
    global result_user
    result_user = database.cursor.fetchone()
    result_name = result_user[2]
    # Если chat_id из сообщения уже есть в таблице, то выводим информацию о пользователе
    if result_name is not None:
        # Отправляем фото и информацию о пользователе
        await bot.send_photo(message.chat.id, result_user[6],
                             caption=f"{languages.languages[result_user[5]]['have_acc']}\n"
                                     f"{languages.languages[result_user[5]]['name']}: {result_user[2]}\n"
                                     f"{languages.languages[result_user[5]]['age']}: {result_user[3]}\n"
                                     f"{languages.languages[result_user[5]]['country']}: {result_user[4]}\n"
                                     f"{languages.languages[result_user[5]]['language']}: {result_user[5]}")
        # Предлагаем пользователю отредактировать информацию
        await message.answer(text=languages.languages[result_user[5]]['edit'], reply_markup=keyboard.inline_edit_kb)
    # Если chat_id из сообщения нет в таблице, то начинаем процесс регистрации
    else:
        # Приветствуем пользователя и запрашиваем его имя
        await message.answer(languages.languages[result_user[5]]['hi'],
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer(languages.languages[result_user[5]]['name_input'])
        await Registration.name.set()


# состояние name
@dp.message_handler(state=Registration.name)
async def get_age(message: types.Message, state: FSMContext):
    # Получаем имя пользователя и переходим к следующему состоянию - запрос возраста
    name = message.text
    await state.update_data(name_answer=name)
    await message.answer(languages.languages[result_user[5]]['age_input'])
    await Registration.age.set()


# состояние age
@dp.message_handler(state=Registration.age)
async def get_country(message: types.Message, state: FSMContext):
    # Получаем возраст пользователя и переходим к следующему состоянию - запрос страны
    age = message.text
    try:
        age = int(age)
        await state.update_data(age_answer=age)
        await message.answer(languages.languages[result_user[5]]['country_input'], reply_markup=keyboard.countries_bt)
        await Registration.country.set()
    except:
        await message.reply(languages.languages[result_user[5]]['not_number'])


# состояние language
@dp.message_handler(state=Registration.country)
async def get_photo(message: types.Message, state: FSMContext):
    country = message.text
    await state.update_data(country_answer=country)
    await message.answer(languages.languages[result_user[5]]['photo_input'])
    await Registration.photo.set()


# Обработка сообщений, которые не являются изображениями в процессе регистрации.
@dp.message_handler(state=Registration.photo)
async def process_wrong_content(message: types.Message):
    await message.reply(languages.languages[result_user[5]]['not_image'])


# Обработчик для сообщений с фотографиями, который сохраняет фото и данные пользователя в базу данных
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Registration.photo)
async def info(message: types.Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    # Сохраняем фото на сервере
    file_path = f"user_images\{message.chat.id}_.jpg"
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
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[result_user[5]]['profile'])
    # Получаем фото пользователя из базы данных и отправляем его вместе с остальными данными
    query = "SELECT photo FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result = database.cursor.fetchone()
    photo = result[0]
    await bot.send_photo(message.chat.id, photo,
                         caption=f"{languages.languages[result_user[5]]['name']}: {name_answer}\n"
                                 f"{languages.languages[result_user[5]]['age']}: {age_answer}\n"
                                 f"{languages.languages[result_user[5]]['country']}: {country_answer}\n"
                                 f"{languages.languages[result_user[5]]['language']}: {result_user[5]}",
                         reply_markup=keyboard.main_menu)
    await state.finish()


# Обработчик команды /start, который отправляет клавиатуру выбора языка
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    query = f"SELECT language FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    lang = database.cursor.fetchone()
    username = message.from_user.username
    if lang is None:
        await bot.send_message(chat_id=message.chat.id, text='Choose language',
                               reply_markup=keyboard.inline_language_kb)
        database.cursor.execute("INSERT INTO registration_table (chat_id, username) VALUES (?, ?)",
                                (message.chat.id, username))
    else:
        await get_name(message, state=None)


@dp.message_handler(text_contains=['Find user'])
async def find_users(message: types.Message):
    await next_user(message)


@dp.message_handler(text_contains=["Next user"])
async def next_user(message: types.Message):
    query = """ SELECT chat_id FROM registration_table WHERE photo IS NOT NULL"""
    database.cursor.execute(query)
    all_users = database.cursor.fetchall()
    all_users.remove((message.chat.id,))
    if not all_users:
        await bot.send_message(chat_id=message.chat.id, text=f'{languages.languages[result_user[5]]["no_users"]}',
                               reply_markup=keyboard.find_users)
    else:
        database.cursor.execute(f"SELECT language FROM registration_table WHERE chat_id = {message.chat.id}")
        global your_lang
        your_lang = database.cursor.fetchone()

        user = random.choice(all_users)
        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, user)
        global result
        result = database.cursor.fetchone()
        photo = result[6]
        await bot.send_photo(message.chat.id, photo,
                             caption=f"{languages.languages[your_lang[0]]['name']}: {result[2]}\n"
                                     f"{languages.languages[your_lang[0]]['age']}: {result[3]}\n"
                                     f"{languages.languages[your_lang[0]]['country']}: {result[4]}\n"
                                     f"{languages.languages[your_lang[0]]['language']}: {result[5]}\n"
                                     f"{languages.languages[your_lang[0]]['chose_next_step']}",
                             reply_markup=keyboard.find_users)


@dp.message_handler(text_contains=["Start communicate"])
async def next_user_command(message: types.Message):
    database.cursor.execute(f"SELECT * FROM likes_table WHERE user_1 = {result[1]} AND user_2 = {message.chat.id}")
    user_2_row = database.cursor.fetchone()
    if user_2_row is not None:
        database.cursor.execute(f"SELECT username FROM registration_table WHERE chat_id = {result[1]}")
        user_2_username = database.cursor.fetchone()
        database.cursor.execute(f"SELECT username FROM registration_table WHERE chat_id = {message.chat.id}")
        user_1_username = database.cursor.fetchone()
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[your_lang[0]]['wants_to_chat'],
                               reply_markup=keyboard.find_users_after_like)
        await bot.send_message(chat_id=message.chat.id,
                               text=f"{languages.languages[your_lang[0]]['link']} @{user_2_username[0]}")
        await bot.send_message(chat_id=result[1],
                               text=f"{languages.languages[result[5]]['link']} @{user_1_username[0]}")
        database.cursor.execute(f"DELETE FROM likes_table WHERE user_1 = {result[1]} AND user_2 = {result[1]}")
        database.cursor.execute(
            f"DELETE FROM likes_table WHERE user_1 = {message.chat.id} AND user_2 = {message.chat.id}")
        database.conn.commit()
    else:
        await bot.send_message(chat_id=message.chat.id, text=languages.languages[your_lang[0]]['request_sent'],
                               reply_markup=keyboard.find_users_after_like)
        database.cursor.execute("INSERT INTO likes_table (user_1, user_2, like) VALUES (?, ?, ?)",
                                (message.chat.id, result[1], 0))

        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, (message.chat.id,))
        res = database.cursor.fetchone()
        await bot.send_photo(result[1], res[6],
                             caption=f"{languages.languages[result[5]]['chat_with_you']}\n"
                                     f"{languages.languages[result[5]]['name']}: {res[2]}\n"
                                     f"{languages.languages[result[5]]['age']}: {res[3]}\n"
                                     f"{languages.languages[result[5]]['country']}: {res[4]}\n"
                                     f"{languages.languages[result[5]]['language']}: {res[5]}\n"
                                     f"{languages.languages[result[5]]['next_step']}",
                             reply_markup=keyboard.find_users)
    database.conn.commit()


@dp.message_handler(text_contains=["Main menu"])
async def menu(message: types.Message):
    query = "SELECT language FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result = database.cursor.fetchone()
    await bot.send_message(chat_id=message.chat.id, text=languages.languages[result[0]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)


@dp.callback_query_handler(text_contains="not_edit")
async def not_edit_profile_btn(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id, text=languages.languages[result_user[5]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


# Определяем обработчик callback_query с текстом, содержащим "edit" и состоянием None
@dp.callback_query_handler(text_contains="edit", state=None)
async def edit_profile_btn(callback: types.CallbackQuery, state: FSMContext):
    # Отправляем пользователю сообщение с просьбой ввести имя
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[result_user[5]]['name_input'])
    # Устанавливаем состояние FSM на "name"
    await Registration.name.set()


# Обработчик нажатий на кнопки с выбором языка
@dp.callback_query_handler(text_contains="english")
async def eng_lang(callback: types.CallbackQuery):
    # Устанавливаем язык пользователя в атрибут объекта languages
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'English' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages["English"]['main_menu'],
                           reply_markup=keyboard.main_menu)
    # Удаляем сообщение с выбором языка
    await callback.message.delete()


# Аналогичные обработчики для других языков
@dp.callback_query_handler(text_contains="french")
async def eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'French' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['French']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="deutsch")
async def eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Deutsch' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Deutsch']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="сhinese")
async def eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Chinese' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Chinese']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="italiano")
async def eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Italiano' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Italiano']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="russian")
async def eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Русский' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Русский']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


# Запуск бота
if __name__ == '__main__':
    print("Bot is running")
    executor.start_polling(dp, skip_updates=True)
