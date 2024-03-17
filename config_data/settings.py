import os
import sqlite3
import telebot

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, SecretStr, StrictStr
from telebot.storage import StateMemoryStorage

load_dotenv() # Загружаем переменное окружение

conn = sqlite3.connect('../Connection.sql', check_same_thread=False)

class SiteSettings(BaseSettings):
    api_key: SecretStr = os.getenv("SITE_API", None)
    host_api: StrictStr = os.getenv("HOST_API", None)
    token: SecretStr = os.getenv("BOT_TOKEN", None)
state_storage = StateMemoryStorage()
tk = SiteSettings()
TOKEN = tk.token.get_secret_value()

bot = telebot.TeleBot(TOKEN, state_storage=state_storage)