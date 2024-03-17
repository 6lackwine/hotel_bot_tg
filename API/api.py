import requests

from config_data.settings import tk, bot


def search_city(city):
    """
    Функция для получения ID локации
    :param city: Город введенный пользователем
    :return: ID локации
    """
    url_location = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": {city}, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    headers = {
        "X-RapidAPI-Key": tk.api_key.get_secret_value(),
        "X-RapidAPI-Host": tk.host_api
    }
    response_location = requests.get(url_location, headers=headers, params=querystring)
    return response_location

def hotels(city, date_from, date_to, adults):
    """
    Функция для получения отелей по введенным данным
    :param adults: Количество взрослых
    :return: Отели с небольшим описанием
    """
    headers = {
        "X-RapidAPI-Key": tk.api_key.get_secret_value(),
        "X-RapidAPI-Host": tk.host_api,
    }
    url_list = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": city},  # id города или локации 936e74c24c7648fd9473e74544742060
        "checkInDate": {  # Дата заезда
            "day": int(date_from[0]),
            "month": int(date_from[1]),
            "year": int(date_from[2]),
        },
        "checkOutDate": {  # Дата выезда
            "day": int(date_to[0]),
            "month": int(date_to[1]),
            "year": int(date_to[2]),
        },
        "rooms": [
            {
                "adults": int(adults),
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 10,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 150,
            "min": 100
        }}
    }
    response_list = requests.post(url_list, json=payload, headers=headers)
    return response_list

def hotel_detail(id_hotel):
    """
    Функция для получения подробной информации об отеле
    :param id_hotel: ID отеля
    :return: Подробную информацию
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_hotel
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": tk.api_key.get_secret_value(),
        "X-RapidAPI-Host": tk.host_api,
    }

    response = requests.post(url, json=payload, headers=headers)
    return response