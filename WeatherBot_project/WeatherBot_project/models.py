from sqlalchemy import Column, Integer, String, Float
from database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    lat = Column(Float)
    lon = Column(Float)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    last_city = Column(String)


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    city_id = Column(Integer)
