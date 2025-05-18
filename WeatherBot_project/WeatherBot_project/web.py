from flask import Flask, render_template
import threading
import json
import os
from datetime import datetime
from weatherBot import load_cities

app = Flask(__name__)
DATA_DIR = "data"
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "requests": 0}


@app.route('/')
def status():
    stats = load_stats()
    cities = load_cities()
    return render_template(
        "status.html",
        status="Running",
        cities_count=len(cities),
        uptime=stats["start_time"],
        requests=stats["requests"]
    )


def run_web():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    from weatherBot import run_bot_wrapper

    bot_thread = threading.Thread(target=run_bot_wrapper)
    bot_thread.daemon = True
    bot_thread.start()

    run_web()
