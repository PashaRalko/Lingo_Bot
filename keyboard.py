from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


main_menu_bt = KeyboardButton('Main menu')
registration_bt = KeyboardButton('Registration')
start_bt = KeyboardButton('Find user')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_menu.row(registration_bt)
main_menu.row(start_bt)

russian_bt = KeyboardButton('Русский')
english_bt = KeyboardButton('English')
french_bt = KeyboardButton('French')
deutsch_bt = KeyboardButton('Deutsch')
italiano_bt = KeyboardButton('Italiano')
сhinese_bt = KeyboardButton('中文')
lang_bt = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
lang_bt.add(russian_bt, english_bt, french_bt, deutsch_bt, italiano_bt, сhinese_bt)

russia_bt = KeyboardButton('Russia')
england_bt = KeyboardButton('England')
france_bt = KeyboardButton('France')
germany_bt = KeyboardButton('Germany')
italian_bt = KeyboardButton('Italian')
china_bt = KeyboardButton('China')
countries_bt = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
countries_bt.add(russia_bt, england_bt, france_bt, germany_bt, italian_bt, china_bt)

next_user_bt = KeyboardButton('Next user')
like_bt = KeyboardButton('Start communicate')
find_users = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users.row(next_user_bt)
find_users.row(like_bt)
find_users.row(main_menu_bt)

find_users_after_like = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users_after_like.row(next_user_bt)
find_users_after_like.row(main_menu_bt)

edit_acc_bt = InlineKeyboardButton('Edit', callback_data='edit󠁧󠁢󠁥')
not_edit_acc_bt = InlineKeyboardButton('Continue ', callback_data='not_edit')
inline_edit_kb = InlineKeyboardMarkup().add(edit_acc_bt, not_edit_acc_bt)

eng_inline_bt = InlineKeyboardButton('English', callback_data='english󠁧󠁢󠁥')
rus_inline_bt = InlineKeyboardButton('Русский ', callback_data='russian')
french_inline_bt = InlineKeyboardButton('French ', callback_data='french')
deutsch_inline_bt = InlineKeyboardButton('Deutsch ', callback_data='deutsch')
italiano_inline_bt = InlineKeyboardButton('Italiano ', callback_data='italiano')
сhinese_inline_bt = InlineKeyboardButton('中文', callback_data='сhinese')

inline_language_kb = InlineKeyboardMarkup().add(eng_inline_bt, rus_inline_bt, french_inline_bt, deutsch_inline_bt,
                                                italiano_inline_bt, сhinese_inline_bt)
