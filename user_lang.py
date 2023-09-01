from aiogram import Bot, Dispatcher, types
import database
import languages
import keyboard
from main import *


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
