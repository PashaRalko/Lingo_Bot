from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main_menu_bt = KeyboardButton('Main menu 🔴')
registration_bt = KeyboardButton('Profile 🖼')
edit_bt = KeyboardButton('Edit profile 📝')
start_bt = KeyboardButton('Find user 🔍')

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_menu.row(registration_bt)
main_menu.row(start_bt)

main_menu_after_rg = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_menu_after_rg.row(edit_bt)
main_menu_after_rg.row(start_bt)

russian_bt = KeyboardButton('Русский 🇷🇺')
english_bt = KeyboardButton('English 🇬🇧')
french_bt = KeyboardButton('French 🇫🇷')
deutsch_bt = KeyboardButton('Deutsch 🇩🇪')
italiano_bt = KeyboardButton('Italiano 🇮🇹')
сhinese_bt = KeyboardButton('中文 🇨🇳')
lang_bt = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
lang_bt.add(russian_bt, english_bt, french_bt, deutsch_bt, italiano_bt, сhinese_bt)

belarus_bt = KeyboardButton('Belarus 🇧🇾')
russia_bt = KeyboardButton('Russia 🇷🇺')
england_bt = KeyboardButton('England 🇬🇧')
france_bt = KeyboardButton('France 🇫🇷')
germany_bt = KeyboardButton('Germany 🇩🇪')
italian_bt = KeyboardButton('Italian 🇮🇹')
china_bt = KeyboardButton('China 🇨🇳')
countries_bt = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
countries_bt.add(belarus_bt, russia_bt, england_bt, france_bt, germany_bt, italian_bt, china_bt)

next_user_bt = KeyboardButton('Next user 👤')
like_bt = KeyboardButton('Start communicate 👋')
# filter_lang = KeyboardButton('Select the language of the interlocutor')
find_users = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users.row(next_user_bt)
find_users.row(like_bt)
# find_users.row(filter_lang)
find_users.row(main_menu_bt)

find_users_without_like = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users_without_like.row(next_user_bt)
# find_users.row(filter_lang)
find_users_without_like.row(main_menu_bt)

find_users_after_like = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
find_users_after_like.row(next_user_bt)
find_users_after_like.row(main_menu_bt)

edit_acc_bt = InlineKeyboardButton('Edit 🖊', callback_data='edit󠁧󠁢󠁥')
not_edit_acc_bt = InlineKeyboardButton('Continue ➡️', callback_data='not_edit')
delete_acc_bt = InlineKeyboardButton('Delete profile 🗑️', callback_data='delete')
change_language = InlineKeyboardButton('Change language 🌐', callback_data='change_language')
sort_peoples = InlineKeyboardButton('Filter peoples 🌐', callback_data='filter_lang')
inline_edit_kb = InlineKeyboardMarkup().add(edit_acc_bt, not_edit_acc_bt, delete_acc_bt, change_language, sort_peoples)

eng_inline_bt = InlineKeyboardButton('English 🇬🇧', callback_data='english󠁧󠁢󠁥')
rus_inline_bt = InlineKeyboardButton('Русский 🇷🇺', callback_data='russian')
french_inline_bt = InlineKeyboardButton('French 🇫🇷', callback_data='french')
deutsch_inline_bt = InlineKeyboardButton('Deutsch 🇩🇪', callback_data='deutsch')
italiano_inline_bt = InlineKeyboardButton('Italiano 🇮🇹', callback_data='italiano')
сhinese_inline_bt = InlineKeyboardButton('中文 🇨🇳', callback_data='сhinese')

inline_language_kb = InlineKeyboardMarkup().add(eng_inline_bt, rus_inline_bt, french_inline_bt, deutsch_inline_bt,
                                                italiano_inline_bt, сhinese_inline_bt)

sort_eng_inline_bt = InlineKeyboardButton('English 🇬🇧', callback_data='sort_en󠁧󠁢󠁥')
sort_rus_inline_bt = InlineKeyboardButton('Русский 🇷🇺', callback_data='sort_ru')
sort_french_inline_bt = InlineKeyboardButton('French 🇫🇷', callback_data='sort_fr')
sort_deutsch_inline_bt = InlineKeyboardButton('Deutsch 🇩🇪', callback_data='sort_du')
sort_italiano_inline_bt = InlineKeyboardButton('Italiano 🇮🇹', callback_data='sort_it')
sort_сhinese_inline_bt = InlineKeyboardButton('中文 🇨🇳', callback_data='sort_ch')
sort_all_languages = InlineKeyboardButton('all languages', callback_data='all')

inline_sort_language_kb = InlineKeyboardMarkup().add(sort_eng_inline_bt,
                                                     sort_rus_inline_bt,
                                                     sort_french_inline_bt,
                                                     sort_deutsch_inline_bt,
                                                     sort_italiano_inline_bt,
                                                     sort_сhinese_inline_bt,
                                                     sort_all_languages)
