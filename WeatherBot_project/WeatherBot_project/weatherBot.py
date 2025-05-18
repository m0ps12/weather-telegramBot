import os
import json
import requests
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки
TELEGRAM = "7001747583:AAG9GqTSywFkMJWp1g4seL2NCS1tzO1a1bk"
OPENWEATHER = "f77e9b05bc179fdd0f87a6a645040141"
DATA_DIR = "data"
CITIES_FILE = os.path.join(DATA_DIR, "cities.txt")
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_cities():
    if os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, "r", encoding="utf-8") as f:
            return {city.strip(): {} for city in f.readlines() if city.strip()}
    return {
        "Москва": {"lat": 55.7558, "lon": 37.6173},
        "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351},
    }


CITIES = load_cities()


def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favorites, f)


ICONS = {
    "ясно": "☀️", "облачно": "☁️", "дождь": "🌧️",
    "снег": "❄️", "туман": "🌫️", "гроза": "⛈️"
}


async def get_weather(city_name: str, forecast: bool = False) -> dict:
    if city_name not in CITIES:
        return {"error": "Город не найден"}

    coords = CITIES[city_name]
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={OPENWEATHER}&units=metric&lang=ru"
        if forecast else
        f"https://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={OPENWEATHER}&units=metric&lang=ru"
    )
    response = requests.get(url)
    return response.json()


async def format_weather(data: dict, city_name: str, forecast: bool = False) -> str:
    if "error" in data:
        return data["error"]

    try:
        if forecast:
            for entry in data['list']:
                if '12:00:00' in entry['dt_txt']:
                    weather_desc = entry['weather'][0]['description']
                    temp = round(entry['main']['temp'])
                    break
        else:
            weather_desc = data['weather'][0]['description']
            temp = round(data['main']['temp'])

        icon = ICONS.get(weather_desc.split()[0], "🌤️")
        return (
            f"{icon} Прогноз в {city_name} на завтра:\n{weather_desc.capitalize()}, {temp}°C"
            if forecast else
            f"{icon} Погода в {city_name}:\n{weather_desc.capitalize()}, {temp}°C"
        )
    except Exception as e:
        return f"Ошибка получения данных: {str(e)}"


def get_main_keyboard(user_id=None):
    favorites = load_favorites()
    fav_cities = favorites.get(str(user_id), [])[:3] if user_id else []

    buttons = [
        ["🌤️ Текущая", "📅 Завтра"],
        ["🎲 Случайный"] + (["⭐ " + fav for fav in fav_cities] if fav_cities else [])
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌦️ Привет! Я покажу погоду в разных городах.\n"
        "Выбери действие:",
        reply_markup=get_main_keyboard(update.effective_user.id)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    favorites = load_favorites()

    if text.startswith("⭐ "):
        city = text[2:]
        if city in CITIES:
            weather_data = await get_weather(city)
            response = await format_weather(weather_data, city)
        else:
            response = "Город не найден"
    elif text == "🎲 Случайный":
        city = random.choice(list(CITIES.keys()))
        weather_data = await get_weather(city)
        response = await format_weather(weather_data, city)
    elif text == "📅 Завтра":
        if 'last_city' in context.user_data:
            weather_data = await get_weather(context.user_data['last_city'], forecast=True)
            response = await format_weather(weather_data, context.user_data['last_city'], forecast=True)
        else:
            response = "Сначала выбери город для текущей погоды"
    elif text == "🌤️ Текущая":
        response = "Выбери город: " + ", ".join(CITIES.keys())
    elif text in CITIES:
        context.user_data['last_city'] = text
        weather_data = await get_weather(text)
        response = await format_weather(weather_data, text)
    else:
        response = "Используй кнопки меню"

    await update.message.reply_text(response, reply_markup=get_main_keyboard(user_id))


async def run_bot():
    application = Application.builder().token(TELEGRAM).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()


def run_bot_wrapper():
    import asyncio
    asyncio.run(run_bot())


def main():
    application = Application.builder().token(TELEGRAM).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
