from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_menu_bt = KeyboardButton('Главное меню')
registration_bt = KeyboardButton('Регистрация')
start_bt = KeyboardButton('Найти собеседника')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_menu.row(registration_bt)
main_menu.row(start_bt)

russian_bt = KeyboardButton('Русский')
english_bt = KeyboardButton('English')
french_bt = KeyboardButton('French')
deutsch_bt = KeyboardButton('Deutsch')
italiano_bt = KeyboardButton('Italiano')
сhinese_bt = KeyboardButton('中文')
lang = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
lang.add(russian_bt, english_bt, french_bt, deutsch_bt, italiano_bt, сhinese_bt)

next_user_bt = KeyboardButton('Следующий пользователь')
like_bt = KeyboardButton('Общаться с этим пользователем!')
find_users = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users.row(next_user_bt)
find_users.row(like_bt)
find_users.row(main_menu_bt)

edit_acc_bt = InlineKeyboardButton('Редактировать', callback_data='edit󠁧󠁢󠁥')
not_edit_acc_bt = InlineKeyboardButton('Оставить ', callback_data='not_edit')
inline_edit_kb = InlineKeyboardMarkup().add(edit_acc_bt, not_edit_acc_bt)

eng_inline_bt = InlineKeyboardButton('English', callback_data='english󠁧󠁢󠁥')
rus_inline_bt = InlineKeyboardButton('Русский ', callback_data='russian')
french_inline_bt = InlineKeyboardButton('French ', callback_data='french')
deutsch_inline_bt = InlineKeyboardButton('Deutsch ', callback_data='deutsch')
italiano_inline_bt = InlineKeyboardButton('Italiano ', callback_data='italiano')
сhinese_inline_bt = InlineKeyboardButton('中文', callback_data='сhinese')

inline_language_kb = InlineKeyboardMarkup().add(eng_inline_bt, rus_inline_bt, french_inline_bt, deutsch_inline_bt,
                                                italiano_inline_bt, сhinese_inline_bt)
