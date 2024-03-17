from urllib.request import urlopen

import peewee
from telebot import types, custom_filters

from API.api import search_city, hotels, hotel_detail
from keyboards.keyboard import markup_pagination, markup_pagination_next, markup_pagination_back, markup
from database.models import initialize_db, Request, db
from config_data.settings import bot, conn
from states.state import MyStates

cursor = conn.cursor()

page = 0

@bot.message_handler(commands=["custom"], state=MyStates.s_start)
def custom(message):
    """
    Функция принимает команду и просит пользователя ввести город, после меняет состояние
    :param message: Команда от Inline кнопки
    :return:
    """
    # with bot.retrieve_data(message.chat.id) as data:
    #     data["s_start"] = cd
    bot.send_message(message.chat.id, "Введите город")
    bot.set_state(message.chat.id, MyStates.s_city, message.chat.id)

@bot.message_handler(state=MyStates.s_city, is_digit=False)
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
        bot.set_state(message.from_user.id, MyStates.s_date_from, message.chat.id)
    except IndexError as ex:
        ex, bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте снова")

@bot.message_handler(state=MyStates.s_city, is_digit=True)
def incorrect_city(message):
    """
    Если пользователь ввел некорректно город, то функция просит ввести название города заново
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Нельзя вводить числа, попробуйте еще раз")

@bot.message_handler(state=MyStates.s_date_from)
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
    bot.set_state(message.from_user.id, MyStates.s_date_to, message.chat.id)

@bot.message_handler(state=MyStates.s_date_to)
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
    bot.set_state(message.from_user.id, MyStates.s_count_human, message.chat.id)

@bot.message_handler(state=MyStates.s_count_human, is_digit=True)
def set_range(message):
    bot.send_message(message.chat.id, "Ушел искать отели. Немного подождите")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["s_count_human"] = message.text
        result = hotels(city=data["s_city"],
               date_from=data["s_date_from"],
               date_to=data["s_date_to"],
               adults=data["s_count_human"])
        for i in result.json().get("data").get("propertySearch").get("properties"):  # Цены
            min_max_price = {}
            try:
                propertyId = i["id"]
                price = dict(i).get("price").get("strikeOut").get("amount")
                hotel_name = i.get("name")
                image = i.get("propertyImage").get("image").get("url")
                print(hotel_name, price)
                min_max_price[hotel_name] = price
                bot.send_photo(message.chat.id, image, f"🏨 Название: {hotel_name}"
                                                       f"\n💵 Цена: {round(price, 0)}$"
                                                       f"\n🆔 ID: {propertyId}")
            except Exception:
                continue
            min_max_price.clear()
    #bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Введите ID отеля о котором хотите узнать подробнее")
    bot.set_state(message.from_user.id, MyStates.s_result, message.chat.id)

@bot.callback_query_handler(func=lambda call: True, state=MyStates.s_result)
def callback_result(call):
    global page
    req = call.data
    with bot.retrieve_data(call.message.chat.id) as data:
        res = data["s_result"].json()['data']['propertyInfo']
        photo = [i['image']['url'] for i in res['propertyGallery']['images']][:5]
        name = res['summary']["name"]
        address = res["summary"]["location"]['address']['addressLine']
        comfort = [i["text"] for i in res["summary"]['amenities']['topAmenities']['items']]
        review = res["reviewInfo"]["summary"]["overallScoreWithDescriptionA11y"]["value"]

        if req == "next_photo":
            if page == len(photo) - 1:
                bot.edit_message_media(reply_markup=markup_pagination_next, chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       media=types.InputMediaPhoto(photo[page],
                                                                   caption=f"Полная информация об отеле:"
                                                                           f"\n🏨 Название отеля: {name}" # {res['summary']['overview']['propertyRating']['rating'] * '⭐️'}
                                                                           f"\n📜 Описание: {res['summary']['tagline']}"
                                                                           #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
                                                                           f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
                                                                           f"\n🌏 Адрес: {address}"
                                                                           f"\n📈 Рейтинг: {review}"))
            elif page < len(photo):
                page = page + 1
                bot.edit_message_media(reply_markup=markup_pagination, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       media=types.InputMediaPhoto(photo[page],
                                                                   caption=f"Полная информация об отеле:"
                                                                           f"\n🏨 Название отеля: {name}"
                                                                           f"\n📜 Описание: {res['summary']['tagline']}"
                                                                           #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
                                                                           f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
                                                                           f"\n🌏 Адрес: {address}"
                                                                           f"\n📈 Рейтинг: {review}"))
        elif req == "previous_photo":
            if page == 0:
                bot.edit_message_media(reply_markup=markup_pagination_back, chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       media=types.InputMediaPhoto(photo[page],
                                                                   caption=f"Полная информация об отеле:"
                                                                           f"\n🏨 Название отеля: {name}"
                                                                           f"\n📜 Описание: {res['summary']['tagline']}"
                                                                           #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
                                                                           f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
                                                                           f"\n🌏 Адрес: {address}"
                                                                           f"\n📈 Рейтинг: {review}"))
            elif page < len(photo):
                page = page - 1
                print(page)
                bot.edit_message_media(reply_markup=markup_pagination,
                                       chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       media=types.InputMediaPhoto(photo[page],
                                                                   caption=f"Полная информация об отеле:"
                                                                           f"\n🏨 Название отеля: {name}"
                                                                           f"\n📜 Описание: {res['summary']['tagline']}"
                                                                           #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
                                                                           f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
                                                                           f"\n🌏 Адрес: {address}"
                                                                           f"\n📈 Рейтинг: {review}"
                                                                   ))
        elif req == "cancel":
            bot.delete_state(call.message.chat.id, call.message.chat.id)
            bot.send_message(call.message.chat.id, "\nВыбери, что тебе нужно найти 👇", reply_markup=markup)


@bot.message_handler(state=MyStates.s_result, content_types=["text", "photo"])
def result(message):
    detail = hotel_detail(message.text)
    res = detail.json()['data']['propertyInfo']['summary']
    ph = [i['image']['url'] for i in detail.json()['data']['propertyInfo']['propertyGallery']['images']]
    photo1 = urlopen(ph[0])

    initialize_db()
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            print("Запросы")
            request = Request.create(
                user_id=message.from_user.id,
                city=data["s_city"],
                name=res['name'],
                dateFrom=data["s_date_from"],
                dateTo=data["s_date_to"],
                price=None,
                number_of_people=data["s_count_human"],
                image=ph[0]
            )
            request.save()
    except peewee.IntegrityError:
        db.close()
    finally:
        db.close()

    try:
        bot.send_photo(message.chat.id, ph[0], f"Полная информация об отеле:"
                                               f"\n🏨 Название отеля: {res['name']}{res['overview']['propertyRating']['rating'] * '⭐️'}"
                                               f"\n📜 Описание: {res['tagline']}"
        # f"\n⭐️ Количество звёзд: {res['overview']['propertyRating']['rating'] * '⭐️'}"
                                               f"\n🌐 Удобства: {''.join(map(str, [i['text'] for i in res['amenities']['topAmenities']['items']]))}"
                                               f"\n🌏 Адрес: {res['location']['address']['addressLine']}"
                                               f"\n📈 Рейтинг: {detail.json()['data']['propertyInfo']['reviewInfo']['summary']['overallScoreWithDescriptionA11y']['value']}",
                       reply_markup=markup_pagination)
    except TypeError:
        bot.send_photo(message.chat.id, ph[0], f"Полная информация об отеле:"
                                               f"\n🏨 Название отеля: {res['name']}"
                                               f"\n📜 Описание: {res['tagline']}"
        # f"\n⭐️ Количество звёзд: {res['overview']['propertyRating']['rating'] * '⭐️'}"
                                               f"\n🌐 Удобства: {''.join(map(str, [i['text'] for i in res['amenities']['topAmenities']['items']]))}"
                                               f"\n🌏 Адрес: {res['location']['address']['addressLine']}"
                                               f"\n📈 Рейтинг: {detail.json()['data']['propertyInfo']['reviewInfo']['summary']['overallScoreWithDescriptionA11y']['value']}",
                       reply_markup=markup_pagination)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["s_result"] = detail

@bot.message_handler(state=MyStates.s_count_human, is_digit=False)
def incorrect_date_from(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите число!")

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())