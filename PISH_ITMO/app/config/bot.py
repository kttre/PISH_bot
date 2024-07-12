from app.config import env

TG_TOKEN = env("TG_TOKEN", cast=str)

LOCALE = env("LOCALE", cast=str, default="ru")
