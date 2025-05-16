from flask import Flask, render_template_string
import threading
from WeatherBot import main as run_bot

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Weather Bot Status</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 20px; background: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Weather Bot Control Panel</h1>
    <div class="status">
        <p>Bot status: <strong>{{ status }}</strong></p>
        <p>Available cities: {{ cities }}</p>
    </div>
</body>
</html>
"""


@app.route('/')
def status():
    cities = ", ".join(CITIES.keys())  # Используйте ваш список городов
    return render_template_string(HTML_TEMPLATE, status="Running", cities=cities)


def run_web():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Запускаем веб-сервер
    run_web()