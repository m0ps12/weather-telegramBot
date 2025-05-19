from database import init_db, SessionLocal
from models import City


def init_cities():
    db = SessionLocal()

    cities_data = [
        {"name": "Москва", "lat": 55.7558, "lon": 37.6173},
        {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351},
    ]

    for city in cities_data:
        if not db.query(City).filter_by(name=city["name"]).first():
            db.add(City(**city))

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
    init_cities()