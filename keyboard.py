from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

registration_bt = KeyboardButton('Регистрация')

registration = ReplyKeyboardMarkup(one_time_keyboard=True)
registration.add(registration_bt)

eng_inline_bt = InlineKeyboardButton('English', callback_data='english 🏴󠁧󠁢󠁥󠁮󠁧󠁿')
rus_inline_bt = InlineKeyboardButton('Русский ', callback_data='russian' + 'U+1F1F7 U+1F1FA')
inline_language_kb = InlineKeyboardMarkup().add(eng_inline_bt, rus_inline_bt)
