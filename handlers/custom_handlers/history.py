from config_data import bot
from database import Request
from keyboards import markup_cancel, markup


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def callback_cancel(call):
    if call.data == "cancel":
        bot.delete_state(call.message.chat.id, call.message.chat.id)
        bot.send_message(call.message.chat.id, "\nВыбери, что тебе нужно найти 👇", reply_markup=markup)

@bot.message_handler(commands=["history"])
def history(message):
    if Request.filter(user_id=message.chat.id) is not None:
        for request in Request.filter(user_id=message.chat.id)[-10:]:
            print(request.dateFrom[2:-2].replace("'", "").replace(",", ".").replace(' ', ''))
            date_from = request.dateFrom[2:-2].replace("'", "").replace(",", ".").replace(' ', '')
            date_to = request.dateTo[2:-2].replace("'", "").replace(",", ".").replace(' ', '')
            bot.send_photo(message.chat.id, request.image, caption=f"Название отеля: {request.name}"
                                                                   f"\nДаты: с {date_from}, по {date_to}"
                                                                   f"\nЦена: {request.price}"
                                                                   f"\nКоличество людей: {request.number_of_people}",
                           reply_markup=markup_cancel)
    else:
        bot.send_message(message.chat.id, "Запросов еще нет")