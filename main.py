from io import BytesIO

from PIL import Image
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


@dp.message_handler(Text("Регистрация"), state=None)
async def get_name(message: types.Message, state: FSMContext):
    await message.answer(languages.languages[languages.user_language]['hi'], reply_markup=types.ReplyKeyboardRemove())
    await message.answer(languages.languages[languages.user_language]['name_input'])
    await Registration.name.set()


@dp.message_handler(state=Registration.name)
async def get_age(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name_answer=name)
    await message.answer(languages.languages[languages.user_language]['age_input'])
    await Registration.age.set()


@dp.message_handler(state=Registration.age)
async def get_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age_answer=age)
    await message.answer(languages.languages[languages.user_language]['country_input'])
    await Registration.country.set()


@dp.message_handler(state=Registration.country)
async def get_age(message: types.Message, state: FSMContext):
    country = message.text
    await state.update_data(country_answer=country)
    await message.answer(languages.languages[languages.user_language]['language_input'])
    await Registration.language.set()


@dp.message_handler(state=Registration.language)
async def get_age(message: types.Message, state: FSMContext):
    language = message.text
    await state.update_data(country_answer=language)
    await message.answer(languages.languages[languages.user_language]['photo_input'])
    await Registration.photo.set()


@dp.message_handler(state=Registration.photo)
async def get_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name_answer = data.get('name_answer')
    age_answer = data.get('age_answer')
    country_answer = data.get('country_answer')
    language_answer = data.get('language_answer')

    image_data = save_image_to_database()

    database.cursor.execute(
        "INSERT INTO images (chat_id, name, age, country, language, photo) VALUES (?, ?, ?, ?, ?, ?)",
        (message.chat.id, name_answer, age_answer, country_answer, language_answer, image_data))
    database.conn.commit()

    database.cursor.execute('SELECT * FROM database')
    k = database.cursor.fetchall()
    print(k)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_image_to_database(message: types.Message):
    file_path = f"user_images\{message.chat.id}.jpg"
    await message.photo[-1].download(file_path)
    with open(file_path, 'rb') as f:
        image_data = f.read()
    return image_data


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Choose language', reply_markup=keyboard.inline_language_kb)


@dp.callback_query_handler(text_contains="english")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'english'
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['registration'],
                           reply_markup=keyboard.registration)
    await callback.message.delete()


@dp.callback_query_handler(text_contains="russian")
async def eng_lang(callback: types.CallbackQuery):
    languages.user_language = 'russian'
    await bot.send_message(callback.from_user.id, text=languages.languages[languages.user_language]['registration'],
                           reply_markup=keyboard.registration)
    await callback.message.delete()


if __name__ == '__main__':
    print("Bot is running")
    executor.start_polling(dp, skip_updates=True)
