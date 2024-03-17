from config_data.settings import bot
from states.state import MyStates


@bot.message_handler(state ="*", commands=["cancel"])
def reset(message):
    bot.send_message(message.chat.id, "Начнем по новому, введите город")
    #bot.send_message(message.chat.id, "Привет, я бот для поиска отелей"
                                      #"\nВыбери, что тебе нужно найти 👇", reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, MyStates.s_start, message.chat.id)