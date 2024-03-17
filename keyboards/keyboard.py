from telebot import types

markup = types.InlineKeyboardMarkup()
markup_cancel = types.InlineKeyboardMarkup()
markup_pagination = types.InlineKeyboardMarkup()
markup_pagination_next = types.InlineKeyboardMarkup()
markup_pagination_back = types.InlineKeyboardMarkup()
markup.row_width = 2

custom_keyboard = types.InlineKeyboardButton("🏨 Задать диапазон", callback_data="custom")
low_keyboard = types.InlineKeyboardButton("💸 Недорогие отели", callback_data="low")
high_keyboard = types.InlineKeyboardButton("💰 Дорогие отели", callback_data="high")
history_keyboard = types.InlineKeyboardButton("📖 История запросов", callback_data="history")
cancel = types.InlineKeyboardButton("🔙 Вернуться назад", callback_data="cancel")
next_photo = types.InlineKeyboardButton("Фото ➡️", callback_data="next_photo")
previous_photo = types.InlineKeyboardButton("⬅️ Фото", callback_data="previous_photo")
book = types.InlineKeyboardButton("💷 Забронировать", callback_data="book")


markup.add(low_keyboard, high_keyboard, custom_keyboard, history_keyboard)
markup_cancel.add(cancel)
markup_pagination.add(next_photo, previous_photo, cancel)
markup_pagination_next.add(previous_photo, cancel)
markup_pagination_back.add(next_photo, cancel)