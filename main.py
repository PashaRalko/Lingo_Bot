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


def request_info(message: types.Message):
    query = "SELECT * FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result = database.cursor.fetchone()
    return result


# Обработчик на сообщение "Регистрация" без текущего состояния (state=None)
@dp.message_handler(Text("Profile 🖼"), state=None)
async def get_name(message: types.Message, state: FSMContext):
    # Получаем первый chat_id из таблицы registration_table
    global result_user
    result_user = request_info(message)
    # Если chat_id из сообщения уже есть в таблице, то выводим информацию о пользователе
    if result_user[2] is not None:
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
    await message.answer(languages.languages[request_info(message)[5]]['age_input'])
    await Registration.age.set()


# состояние age
@dp.message_handler(state=Registration.age)
async def get_country(message: types.Message, state: FSMContext):
    # Получаем возраст пользователя и переходим к следующему состоянию - запрос страны
    age = message.text
    try:
        age = int(age)
        await state.update_data(age_answer=age)
        await message.answer(languages.languages[request_info(message)[5]]['country_input'],
                             reply_markup=keyboard.countries_bt)
        await Registration.country.set()
    except:
        await message.reply(languages.languages[request_info(message)[5]]['not_number'])


# состояние language
@dp.message_handler(state=Registration.country)
async def get_photo(message: types.Message, state: FSMContext):
    country = message.text
    await state.update_data(country_answer=country)
    await message.answer(languages.languages[request_info(message)[5]]['photo_input'])
    await Registration.photo.set()


# Обработка сообщений, которые не являются изображениями в процессе регистрации.
@dp.message_handler(state=Registration.photo)
async def process_wrong_content(message: types.Message):
    await message.reply(languages.languages[request_info(message)[5]]['not_image'])


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
                         caption=f"{languages.languages[request_info(message)[5]]['name']}: {name_answer}\n"
                                 f"{languages.languages[request_info(message)[5]]['age']}: {age_answer}\n"
                                 f"{languages.languages[request_info(message)[5]]['country']}: {country_answer}\n"
                                 f"{languages.languages[request_info(message)[5]]['language']}: {result_user[5]}",
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
        database.cursor.execute("INSERT INTO registration_table (chat_id, username, filter_language) VALUES (?, ?, ?)",
                                (message.chat.id, username, 'all languages'))
    else:
        await get_name(message, state=None)


@dp.message_handler(text_contains=['Find user 🔍'])
async def find_users(message: types.Message):
    await next_user(message)


@dp.message_handler(text_contains=["Next user 👤"])
async def next_user(message: types.Message):
    database.cursor.execute(f"SELECT filter_language FROM registration_table WHERE chat_id = {message.chat.id}")
    filter_language = database.cursor.fetchone()[0]
    if filter_language != 'all languages':
        query = f""" SELECT chat_id FROM registration_table WHERE photo IS NOT NULL AND language = '{filter_language}'"""
    else:
        query = f""" SELECT chat_id FROM registration_table WHERE photo IS NOT NULL"""
    database.cursor.execute(query)
    all_users = database.cursor.fetchall()
    if (message.chat.id,) in all_users:
        all_users.remove((message.chat.id,))
    if not all_users:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'{languages.languages[request_info(message)[5]]["no_users"]}',
                               reply_markup=keyboard.find_users)
    else:
        user = random.choice(all_users)
        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, user)
        global result_user_info
        result_user_info = database.cursor.fetchone()
        photo = result_user_info[6]
        await bot.send_photo(message.chat.id, photo,
                             caption=f"{languages.languages[request_info(message)[5]]['name']}: {result_user_info[2]}\n"
                                     f"{languages.languages[request_info(message)[5]]['age']}: {result_user_info[3]}\n"
                                     f"{languages.languages[request_info(message)[5]]['country']}: {result_user_info[4]}\n"
                                     f"{languages.languages[request_info(message)[5]]['language']}: {result_user_info[5]}\n"
                                     f"{languages.languages[request_info(message)[5]]['chose_next_step']}",
                             reply_markup=keyboard.find_users)


@dp.message_handler(text_contains=["Start communicate 👋"])
async def next_user_command(message: types.Message):
    database.cursor.execute(
        f"SELECT * FROM likes_table WHERE user_1 = {result_user_info[1]} AND user_2 = {message.chat.id}")
    user_2_row = database.cursor.fetchone()
    if user_2_row is not None:
        database.cursor.execute(f"SELECT username FROM registration_table WHERE chat_id = {result_user_info[1]}")
        user_2_username = database.cursor.fetchone()
        database.cursor.execute(f"SELECT username FROM registration_table WHERE chat_id = {message.chat.id}")
        user_1_username = database.cursor.fetchone()
        await bot.send_message(chat_id=message.chat.id,
                               text=f"{languages.languages[request_info(message)[5]]['link']} @{user_2_username[0]}")
        await bot.send_message(chat_id=result_user_info[1],
                               text=f"{languages.languages[result_user_info[5]]['link']} @{user_1_username[0]}")
        database.cursor.execute(
            f"DELETE FROM likes_table WHERE user_1 = {message.chat.id} AND user_2 = {result_user_info[1]}")
        database.cursor.execute(
            f"DELETE FROM likes_table WHERE user_1 = {result_user_info[1]} AND user_2 = {message.chat.id}")
        database.conn.commit()
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=languages.languages[request_info(message)[5]]['request_sent'],
                               reply_markup=keyboard.find_users_after_like)
        database.cursor.execute("INSERT INTO likes_table (user_1, user_2, like) VALUES (?, ?, ?)",
                                (message.chat.id, result_user_info[1], 0))

        query = "SELECT * FROM registration_table WHERE chat_id = ?"
        database.cursor.execute(query, (message.chat.id,))
        res = database.cursor.fetchone()
        await bot.send_photo(result_user_info[1], res[6],
                             caption=f"{languages.languages[result_user_info[5]]['chat_with_you']}\n"
                                     f"{languages.languages[result_user_info[5]]['name']}: {res[2]}\n"
                                     f"{languages.languages[result_user_info[5]]['age']}: {res[3]}\n"
                                     f"{languages.languages[result_user_info[5]]['country']}: {res[4]}\n"
                                     f"{languages.languages[result_user_info[5]]['language']}: {res[5]}\n"
                                     f"{languages.languages[result_user_info[5]]['next_step']}",
                             reply_markup=keyboard.find_users)
    database.conn.commit()


@dp.message_handler(text_contains=["Main menu 🔴"])
async def menu(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text=languages.languages[request_info(message)[5]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)


def request(message: types.Message):
    query = "SELECT language FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (message.chat.id,))
    result = database.cursor.fetchone()
    return result


@dp.message_handler(commands=None)
async def handle_invalid_command(message: types.Message):
    if request(message) is None:
        await message.reply(languages.languages[request_info(message)[5]]['dont_have_acc'])
    else:
        await message.reply(languages.languages[request_info(message)[5]]['unknown_command'])


def request_callbck(callback: types.CallbackQuery):
    query = "SELECT * FROM registration_table WHERE chat_id = ?"
    database.cursor.execute(query, (callback.from_user.id,))
    result = database.cursor.fetchone()
    return result


@dp.callback_query_handler(text_contains="not_edit")
async def not_edit_profile_btn(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['main_menu_back'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="filter_lang")
async def filter_lang(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['main_menu_back'],
                           reply_markup=keyboard.inline_sort_language_kb)


# Определяем обработчик callback_query с текстом, содержащим "edit" и состоянием None
@dp.callback_query_handler(text_contains="edit", state=None)
async def edit_profile_btn(callback: types.CallbackQuery, state: FSMContext):
    # Отправляем пользователю сообщение с просьбой ввести имя
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['name_input'])
    # Устанавливаем состояние FSM на "name"
    await Registration.name.set()


@dp.callback_query_handler(text_contains="delete")
async def edit_profile_btn(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['acc_delete'])
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    database.cursor.execute(
        f"DELETE FROM registration_table WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()


@dp.callback_query_handler(text_contains="change_language")
async def edit_profile_btn(callback: types.CallbackQuery):
    # Отправляем пользователю сообщение с просьбой выбрать язык
    await bot.send_message(chat_id=callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['change_user_language'],
                           reply_markup=keyboard.inline_language_kb)


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
async def fr_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'French' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['French']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="deutsch")
async def du_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Deutsch' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Deutsch']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="сhinese")
async def ch_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Chinese' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Chinese']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="italiano")
async def it_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Italiano' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Italiano']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="russian")
async def ru_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET language = 'Русский' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id, text=languages.languages['Русский']['main_menu'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_en")
async def sort_eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'English' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    # Удаляем сообщение с выбором языка
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_ru")
async def sort_eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'Русский' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_fr")
async def sort_fr_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'French' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_du")
async def sort_du_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'Deutsch' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_сh")
async def sort_ch_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'Chinese' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="sort_it")
async def sort_it_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'Italiano' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['user_language_set'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="all")
async def sort_eng_lang(callback: types.CallbackQuery):
    database.cursor.execute(
        f"UPDATE registration_table SET filter_language = 'all languages' WHERE chat_id = {callback.from_user.id}")
    database.conn.commit()
    # Отправляем сообщение с текстом на выбранном языке и клавиатурой регистрации
    await bot.send_message(callback.from_user.id,
                           text=languages.languages[request_callbck(callback)[5]]['all_users'],
                           reply_markup=keyboard.main_menu)
    await callback.message.delete()


# Запуск бота
if __name__ == '__main__':
    print("Bot is running")
    executor.start_polling(dp, skip_updates=True)
