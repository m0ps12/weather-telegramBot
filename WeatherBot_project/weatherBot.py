import requests
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# tokens
TELEGRAM = "7001747583:AAG9GqTSywFkMJWp1g4seL2NCS1tzO1a1bk"
OPENWEATHER = "f77e9b05bc179fdd0f87a6a645040141"

CITIES = {
    "Москва": {"lat": 55.7558, "lon": 37.6173},
    "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351},
    "Сочи": {"lat": 43.5855, "lon": 39.7231},
    "Нью-Йорк": {"lat": 40.7128, "lon": -74.0060},
    "Токио": {"lat": 35.6762, "lon": 139.6503},
    "Париж": {"lat": 48.8566, "lon": 2.3522},
    "Лондон": {"lat": 51.5074, "lon": -0.1278},
    "Берлин": {"lat": 52.5200, "lon": 13.4050},
    "Пекин": {"lat": 39.9042, "lon": 116.4074},
    "Стамбул": {"lat": 41.0082, "lon": 28.9784}
}

ICONS = {
    "ясно": "☀️",
    "облачно": "☁️",
    "дождь": "🌧️",
    "снег": "❄️",
    "туман": "🌫️"
}


# данные
async def get_weather(city_name: str, forecast: bool = False) -> dict:
    coords = CITIES[city_name]
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={OPENWEATHER}&units=metric&lang=ru"
        if forecast else
        f"https://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={OPENWEATHER}&units=metric&lang=ru"
    )
    response = requests.get(url)
    return response.json()


# вывод погоды

async def format_weather(data: dict, city_name: str, forecast: bool = False) -> str:
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


# кнопки
def get_keyboard():
    buttons = [
        ["🌤️ Текущая погода", "📅 Завтра"],
        ["🎲 Случайный город"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


# приветствие

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🌦️ Привет! Я покажу погоду в любом из 20 популярных городов.\n"
        "Выбери действие:",
        reply_markup=get_keyboard()
    )


# сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🎲 Случайный город":
        city = random.choice(list(CITIES.keys()))
        weather_data = await get_weather(city)
        response = await format_weather(weather_data, city)

    elif text == "📅 Завтра":
        if 'last_city' in context.user_data:
            weather_data = await get_weather(context.user_data['last_city'], forecast=True)
            response = await format_weather(weather_data, context.user_data['last_city'], forecast=True)
        else:
            response = "Сначала выбери город для текущей погоды"

    elif text == "🌤️ Текущая погода":
        response = "Выбери город из списка: " + ", ".join(CITIES.keys())

    elif text in CITIES:
        context.user_data['last_city'] = text
        weather_data = await get_weather(text)
        response = await format_weather(weather_data, text)

    else:
        response = "Используй кнопки меню"

    await update.message.reply_text(response, reply_markup=get_keyboard())


# zapusk
def main() -> None:
    application = Application.builder().token(TELEGRAM).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
