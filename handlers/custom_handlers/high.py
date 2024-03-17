import peewee

from API import search_city, hotels
from config_data import bot
from database import Request, db, initialize_db
from keyboards import markup_cancel, markup
from states import HighStates


@bot.message_handler(commands=["high"], state=HighStates.s_start)
def high(message):
    """
    Функция принимает команду и просит пользователя ввести город, после меняет состояние
    :param message: Команда от Inline кнопки
    :return:
    """
    # with bot.retrieve_data(message.chat.id) as data:
    #     data["s_start"] = cd
    bot.send_message(message.chat.id, "Введите город")
    bot.set_state(message.chat.id, HighStates.s_city, message.chat.id)

@bot.message_handler(state=HighStates.s_city, is_digit=False)
def get_city(message):
    """
    Функция принимает введенный пользователем город, обрабатывает и получает ID локации. Сохраняет результат и
    просит ввести дату заезда в отель, затем меняет состояние
    :param message: Город
    :return:
    """
    # Добавить проверку try exept на правильность города
    print(message.text)
    bot.send_message(message.chat.id, "Введите дату заезда")
    city = message.text.strip().lower()
    try:
        result_city = search_city(city)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["s_city"] = result_city.json()["sr"][0]["gaiaId"]
            print(data["s_city"])
        bot.set_state(message.from_user.id, HighStates.s_date_from, message.chat.id)
    except IndexError as ex:
        ex, bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте снова")

@bot.message_handler(state=HighStates.s_city, is_digit=True)
def incorrect_city(message):
    """
    Если пользователь ввел некорректно город, то функция просит ввести название города заново
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Нельзя вводить числа, попробуйте еще раз")

@bot.message_handler(state=HighStates.s_date_from)
def get_date_from(message):
    """
    Функция принимает введенную дату заезда, сохраняет ее и просит ввести дату выезда, после меняет состояние
    :param message: Дата заезда
    :return:
    """
    print(message.text)
    bot.send_message(message.chat.id, "Введите дату выезда")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["s_date_from"] = message.text.split(".")
    bot.set_state(message.from_user.id, HighStates.s_date_to, message.chat.id)

@bot.message_handler(state=HighStates.s_date_to)
def get_date_to(message):
    """
    Функция принимает дату выезда, сохраняет ее и просит ввести количество взрослых, после меняет состояние
    :param message: Дата выезда
    :return:
    """
    print(message.text)
    bot.send_message(message.chat.id, "Введите количество взрослых")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["s_date_to"] = message.text.split(".")
    bot.set_state(message.from_user.id, HighStates.s_count_human, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def callback_cancel(call):
    if call.data == "cancel":
        bot.delete_state(call.message.chat.id, call.message.chat.id)
        bot.send_message(call.message.chat.id, "\nВыбери, что тебе нужно найти 👇", reply_markup=markup)

@bot.message_handler(state=HighStates.s_count_human, is_digit=True)
def set_range(message):
    min_max_price = []
    min_max_image = []
    min_max_name = []
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["s_count_human"] = message.text
            result = hotels(city=data["s_city"],
                   date_from=data["s_date_from"],
                   date_to=data["s_date_to"],
                   adults=data["s_count_human"])
            for i in result.json().get("data").get("propertySearch").get("properties"):  # Цены
                try:
                    propertyId = i["id"]
                    price = dict(i).get("price").get("strikeOut").get("amount")
                    hotel_name = i.get("name")
                    image = i.get("propertyImage").get("image").get("url")
                    print(hotel_name, price)
                    min_max_price.append(int(price))
                    min_max_name.append(hotel_name)
                    min_max_image.append(image)
                    #bot.send_photo(message.chat.id, image, f"🏨 Название: {hotel_name}"
                                                           #f"\n💵 Цена: {round(price, 0)}$"
                                                           #f"\n🆔 ID: {propertyId}")
                    try:
                        print("Запросы")
                        req = Request.create(
                            user_id=message.from_user.id,
                            city=data["s_city"],
                            dateFrom=data["s_dateFrom"],
                            dateTo=data["s_dateTo"],
                            minPrice=min(min_max_price),
                            maxPrice=max(min_max_price),
                            number_of_people=data["s_count_human"],
                        )
                        print("Запросы 2", data["s_city"], min(min_max_price))
                        req.save()
                    except peewee.IntegrityError:
                        db.close()
                except Exception:
                    continue
            i = min_max_price.index(max(min_max_price))
            print(min_max_price)
            initialize_db()
            try:
                print("Запросы")
                req = Request.create(
                    user_id=message.from_user.id,
                    city=data["s_city"],
                    name=min_max_name[i],
                    dateFrom=data["s_date_from"],
                    dateTo=data["s_date_to"],
                    minPrice=None,
                    maxPrice=int(max(min_max_price)),
                    number_of_people=data["s_count_human"],
                    image=min_max_image[i]
                )
                print("Запросы 2")
                req.save()
            except peewee.IntegrityError:
                print("EXCEPT")
                db.close()
            finally:
                db.close()
            bot.send_photo(message.chat.id, min_max_image[i], f"🏨 Название: {min_max_name[i]}"
                                                              f"\n💵 Цена: {max(min_max_price)}$",
                           reply_markup=markup_cancel)
            min_max_price.clear()
    except TypeError:
        bot.send_message(message.chat.id, "Что то пошло не так, попробуйте заново")
    bot.delete_state(message.from_user.id, message.chat.id)