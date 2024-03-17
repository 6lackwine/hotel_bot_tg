# from urllib.request import urlopen
#
# from keyboards.keyboard import markup, markup_pagination, markup_pagination_next, markup_pagination_back
#
# import peewee
# import requests
#
# from telebot.storage import StateMemoryStorage
# from telebot import custom_filters, types
# import telebot
#
# from database.models import User, initialize_db, db, Request
# from config_data.settings import SiteSettings, conn
#
# state_storage = StateMemoryStorage()
#
# tk = SiteSettings()
# TOKEN = tk.token.get_secret_value()
#
# bot = telebot.TeleBot(TOKEN, state_storage=state_storage)
#
# #conn = sqlite3.connect('Connection.sql', check_same_thread=False)
# cursor = conn.cursor()
#
# page = 0
#
# @bot.callback_query_handler(func=lambda call: call.data == "custom")
# def callback_query_custom(call):
#     if call.data == "custom":
#         custom(call.message)
#         #bot.answer_callback_query(call.id, "Диапазон")
#
# @bot.callback_query_handler(func=lambda call: call.data == "low")
# def callback_query_low(call):
#     if call.data == "low":
#         # with bot.retrieve_data(call.message.chat.id) as data:
#         #     data["s_start"] = call.data
#         low(call.message)
#
# @bot.callback_query_handler(func=lambda call: call.data == "high")
# def callback_query_high(call):
#     if call.data == "high":
#         pass
#
# @bot.callback_query_handler(func=lambda call: call.data == "history")
# def callback_query_history(call):
#     if call.data == "history":
#         pass
#
# @bot.message_handler(commands=["low"])
# def low(message):
#     bot.send_message(message.chat.id, "Введите город")
#     search_city(message)
#     bot.set_state(message.chat.id, states.MyStates.s_city, message.chat.id)
#
# @bot.message_handler(commands=["custom"])
# def custom(message):
#     bot.send_message(message.chat.id, "Введите город")
#     bot.set_state(message.chat.id, states.MyStates.s_city, message.chat.id)
#
# @bot.message_handler(state ="*", commands=["cancel"])
# def reset(message):
#     bot.send_message(message.chat.id, "Начнем по новому, введите город")
#     #bot.send_message(message.chat.id, "Привет, я бот для поиска отелей"
#                                       #"\nВыбери, что тебе нужно найти 👇", reply_markup=markup)
#     bot.delete_state(message.from_user.id, message.chat.id)
#     bot.set_state(message.from_user.id, states.MyStates.s_start, message.chat.id)
#
# def search_city(city):
#     url_location = "https://hotels4.p.rapidapi.com/locations/v3/search"
#     querystring = {"q": {city}, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
#     headers = {
#         "X-RapidAPI-Key": tk.api_key.get_secret_value(),
#         "X-RapidAPI-Host": tk.host_api
#     }
#     response_location = requests.get(url_location, headers=headers, params=querystring)
#     return response_location
#
# @bot.message_handler(state=states.MyStates.s_city, is_digit=False)
# def get_city(message):
#     # Добавить проверку try exept на правильность города
#     print(message.text)
#     bot.send_message(message.chat.id, "Введите дату заезда")
#     city = message.text.strip().lower()
#     result_city = search_city(city)
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data["s_city"] = result_city.json()["sr"][0]["gaiaId"]
#         print(data["s_city"])
#     #if data["s_start"] == "custom":
#     bot.set_state(message.from_user.id, states.MyStates.s_date_from, message.chat.id)
#     # elif data["s_start"] == "/low":
#     #     pass
#     # elif data["s_start"] == "/high":
#     #     pass
#
# @bot.message_handler(state=states.MyStates.s_city, is_digit=True)
# def incorrect_city(message):
#     bot.send_message(message.chat.id, "Введен некорректно город, попробуйте еще раз")
#
# @bot.message_handler(state=states.MyStates.s_date_from)
# def get_date_from(message):
#     print(message.text)
#     bot.send_message(message.chat.id, "Введите дату выезда")
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data["s_date_from"] = message.text.split(".")
#     bot.set_state(message.from_user.id, states.MyStates.s_date_to, message.chat.id)
#
# @bot.message_handler(state=states.MyStates.s_date_to)
# def get_date_to(message):
#     print(message.text)
#     bot.send_message(message.chat.id, "Введите количество взрослых")
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data["s_date_to"] = message.text.split(".")
#     bot.set_state(message.from_user.id, states.MyStates.s_count_human, message.chat.id)
#
# @bot.message_handler(state=states.MyStates.s_count_human, is_digit=True)
# def set_range(message):
#     headers = {
#         "X-RapidAPI-Key": tk.api_key.get_secret_value(),
#         "X-RapidAPI-Host": tk.host_api,
#     }
#     url_list = "https://hotels4.p.rapidapi.com/properties/v2/list"
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data["s_count_human"] = message.text
#         print("RESULT:", data["s_city"], data["s_date_from"], data["s_date_to"], data["s_count_human"])
#         payload = {
#             "currency": "USD",
#             "eapid": 1,
#             "locale": "en_US",
#             "siteId": 300000001,
#             "destination": {"regionId": data["s_city"]},  # id города или локации 936e74c24c7648fd9473e74544742060
#             "checkInDate": {  # Дата заезда
#                 "day": int(data["s_date_from"][0]),
#                 "month": int(data["s_date_from"][1]),
#                 "year": int(data["s_date_from"][2]),
#             },
#             "checkOutDate": {  # Дата выезда
#                 "day": int(data["s_date_to"][0]),
#                 "month": int(data["s_date_to"][1]),
#                 "year": int(data["s_date_to"][2]),
#             },
#             "rooms": [
#                 {
#                     "adults": int(data["s_count_human"]),
#                     "children": [{"age": 5}, {"age": 7}]
#                 }
#             ],
#             "resultsStartingIndex": 0,
#             "resultsSize": 10,
#             "sort": "PRICE_LOW_TO_HIGH",
#             "filters": {"price": {
#                 "max": 150,
#                 "min": 100
#             }}
#         }
#         print(payload)
#         response_list = requests.post(url_list, json=payload, headers=headers)
#         print(response_list.json())
#         #print(response_list.json().get("data").get("propertySearch").get("filterMetadata").get("neighborhoods")) # Районы города
#         #print(response_list.json().get("data").get("propertySearch").get("filterMetadata").get("priceRange"))Диапазон цен
#         for i in response_list.json().get("data").get("propertySearch").get("properties"): # Цены
#             min_max_price = {}
#             try:
#                 propertyId = i["id"]
#                 price = dict(i).get("price").get("strikeOut").get("amount")
#                 hotel_name = i.get("name")
#                 image = i.get("propertyImage").get("image").get("url")
#                 print(hotel_name, price)
#                 min_max_price[hotel_name] = price
#                 bot.send_photo(message.chat.id, image, f"🏨 Название: {hotel_name}"
#                                                        f"\n💵 Цена: {round(price, 0)}$"
#                                                        f"\n🆔 ID: {propertyId}")
#                 initialize_db()
#                 try:
#                     print("Запросы")
#                     req = Request.create(
#                                          user_id=message.from_user.id,
#                                          city=data["s_city"],
#                                          dateFrom=data["s_dateFrom"],
#                                          dateTo=data["s_dateTo"],
#                                          minPrice=min(min_max_price),
#                                          maxPrice=max(min_max_price),
#                                          number_of_people=data["s_count_human"],
#                                          )
#                     print("Запросы 2", data["s_city"], min(min_max_price))
#                     req.save()
#                 except peewee.IntegrityError:
#                     db.close()
#             except Exception:
#                 continue
#             min_max_price.clear()
#     bot.delete_state(message.from_user.id, message.chat.id)
#     bot.send_message(message.chat.id, "Введите ID отеля о котором хотите узнать подробнее")
#     bot.set_state(message.from_user.id, states.MyStates.s_result, message.chat.id)
#
# @bot.callback_query_handler(func=lambda call: True)
# def callback_result(call):
#     global page
#     req = call.data
#     with bot.retrieve_data(call.message.chat.id) as data:
#         res = data["s_result"].json()['data']['propertyInfo']
#         photo = [i['image']['url'] for i in res['propertyGallery']['images']][:5]
#         name = res['summary']["name"]
#         address = res["summary"]["location"]['address']['addressLine']
#         comfort = [i["text"] for i in res["summary"]['amenities']['topAmenities']['items']]
#         review = res["reviewInfo"]["summary"]["overallScoreWithDescriptionA11y"]["value"]
#
#         if req == "next_photo":
#             if page == len(photo) - 1:
#                 bot.edit_message_media(reply_markup=markup_pagination_next, chat_id=call.message.chat.id,
#                                        message_id=call.message.message_id,
#                                        media=types.InputMediaPhoto(photo[page],
#                                                                    caption=f"Полная информация об отеле:"
#                                                                            f"\n🏨 Название отеля: {name}{res['summary']['overview']['propertyRating']['rating'] * '⭐️'}"
#                                                                            f"\n📜 Описание: {res['summary']['tagline']}"
#                                                                            #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
#                                                                            f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
#                                                                            f"\n🌏 Адрес: {address}"
#                                                                            f"\n📈 Рейтинг: {review}"))
#             elif page < len(photo):
#                 page = page + 1
#                 print("PAGE", page)
#                 print("LEN PHOTO", len(photo))
#                 bot.edit_message_media(reply_markup=markup_pagination, chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                        media=types.InputMediaPhoto(photo[page],
#                                                                    caption=f"Полная информация об отеле:"
#                                                                            f"\n🏨 Название отеля: {name}{res['summary']['overview']['propertyRating']['rating'] * '⭐️'}"
#                                                                            f"\n📜 Описание: {res['summary']['tagline']}"
#                                                                            #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
#                                                                            f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
#                                                                            f"\n🌏 Адрес: {address}"
#                                                                            f"\n📈 Рейтинг: {review}"))
#         elif req == "previous_photo":
#             if page == 0:
#                 bot.edit_message_media(reply_markup=markup_pagination_back, chat_id=call.message.chat.id,
#                                        message_id=call.message.message_id,
#                                        media=types.InputMediaPhoto(photo[page],
#                                                                    caption=f"Полная информация об отеле:"
#                                                                            f"\n🏨 Название отеля: {name}{res['summary']['overview']['propertyRating']['rating'] * '⭐️'}"
#                                                                            f"\n📜 Описание: {res['summary']['tagline']}"
#                                                                            #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
#                                                                            f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
#                                                                            f"\n🌏 Адрес: {address}"
#                                                                            f"\n📈 Рейтинг: {review}"))
#             elif page < len(photo):
#                 page = page - 1
#                 print(page)
#                 bot.edit_message_media(reply_markup=markup_pagination,
#                                        chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                        media=types.InputMediaPhoto(photo[page],
#                                                                    caption=f"Полная информация об отеле:"
#                                                                            f"\n🏨 Название отеля: {name}{res['summary']['overview']['propertyRating']['rating'] * '⭐️'}"
#                                                                            f"\n📜 Описание: {res['summary']['tagline']}"
#                                                                            #f"\n⭐️ Количество звёзд: {res['summary']['overview']['propertyRating']['accessibility']}"
#                                                                            f"\n🌐 Удобства: {', '.join(map(str, comfort))}"
#                                                                            f"\n🌏 Адрес: {address}"
#                                                                            f"\n📈 Рейтинг: {review}"
#                                                                    ))
#
# @bot.message_handler(state=states.MyStates.s_result, content_types=["text", "photo"])
# def result(message):
#     url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
#     payload = {
#         "currency": "USD",
#         "eapid": 1,
#         "locale": "en_US",
#         "siteId": 300000001,
#         "propertyId": message.text
#     }
#     headers = {
#         "content-type": "application/json",
#         "X-RapidAPI-Key": tk.api_key.get_secret_value(),
#         "X-RapidAPI-Host": tk.host_api,
#     }
#
#     response = requests.post(url, json=payload, headers=headers)
#     res = response.json()['data']['propertyInfo']['summary']
#     #stars = res['overview']['propertyRating']['accessibility']
#
#     ph = [i['image']['url'] for i in response.json()['data']['propertyInfo']['propertyGallery']['images']]
#     photo1 = urlopen(ph[0])
#     bot.send_photo(message.chat.id, ph[0], f"Полная информация об отеле:"
#                                       f"\n🏨 Название отеля: {res['name']}{res['overview']['propertyRating']['rating'] * '⭐️'}"
#                                       f"\n📜 Описание: {res['tagline']}"
#                                       #f"\n⭐️ Количество звёзд: {res['overview']['propertyRating']['rating'] * '⭐️'}"
#                                       f"\n🌐 Удобства: {''.join(map(str, [i['text'] for i in res['amenities']['topAmenities']['items']]))}"
#                                       f"\n🌏 Адрес: {res['location']['address']['addressLine']}"
#                                       f"\n📈 Рейтинг: {response.json()['data']['propertyInfo']['reviewInfo']['summary']['overallScoreWithDescriptionA11y']['value']}",
#                    reply_markup=markup_pagination)
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data["s_result"] = response
#
# @bot.message_handler(state=states.MyStates.s_count_human, is_digit=False)
# def incorrect_date_from(message):
#     bot.send_message(message.chat.id, "Пожалуйста, введите число!")
#
# @bot.message_handler(content_types=["text"])
# def help_commands(message):
#     if message.text.lower() == "привет":
#         bot.send_message(message.chat.id, "Привет, я бот для поиска отелей"
#                                           "\nВыбери, что тебе нужно найти 👇", reply_markup=markup)
#         initialize_db()
#         try:
#             user = User.create(user_id=message.from_user.id, name=message.from_user.first_name)
#             user.save()
#         except peewee.IntegrityError:
#             db.close()
#     else:
#         bot.reply_to(message, "Я тебя не понимаю, напиши привет")
#
# bot.add_custom_filter(custom_filters.StateFilter(bot))
# bot.add_custom_filter(custom_filters.IsDigitFilter())
#
# if __name__ == "__main__":
#     bot.infinity_polling()