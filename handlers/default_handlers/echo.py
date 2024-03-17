import peewee
from telebot import custom_filters

from handlers.custom_handlers.custom import custom
from handlers.custom_handlers.high import high
from handlers.custom_handlers.history import history
from handlers.custom_handlers.low import low
from keyboards.keyboard import markup
from database.models import initialize_db, User, db
from config_data.settings import bot
from states import MyStates, LowStates, HighStates


@bot.callback_query_handler(func=lambda call: call.data == "custom")
def callback_query_custom(call):
    if call.data == "custom":
        bot.set_state(call.message.chat.id, MyStates.s_start, call.message.chat.id)
        custom(call.message)
        #bot.answer_callback_query(call.id, "Диапазон")

@bot.callback_query_handler(func=lambda call: call.data == "low")
def callback_query_low(call):
    if call.data == "low":
        bot.set_state(call.message.chat.id, LowStates.s_start, call.message.chat.id)
        low(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "high")
def callback_query_high(call):
    if call.data == "high":
        bot.set_state(call.message.chat.id, HighStates.s_start, call.message.chat.id)
        high(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "history")
def callback_query_history(call):
    if call.data == "history":
        history(call.message)

@bot.message_handler(content_types=["text"])
def help_commands(message):
    if message.text.lower() == "привет":
        bot.send_message(message.chat.id, "Привет, я бот для поиска отелей"
                                          "\nВыбери, что тебе нужно найти 👇", reply_markup=markup)
        initialize_db()
        try:
            user = User.create(user_id=message.from_user.id, name=message.from_user.first_name)
            user.save()
        except peewee.IntegrityError:
            db.close()
        finally:
            db.close()
    else:
        bot.reply_to(message, "Я тебя не понимаю, напиши привет")

state_filter = bot.add_custom_filter(custom_filters.StateFilter(bot))
is_digit_filter = bot.add_custom_filter(custom_filters.IsDigitFilter())

if __name__ == "__main__":
    bot.infinity_polling()