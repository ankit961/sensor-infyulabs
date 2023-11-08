import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "8f7c95ef3e6507753ea648c4659c36f1"
    SQLALCHEMY_DATABASE_URI = "postgresql://infyulabs:infyulabs123@/sensors?host=/cloudsql/sensor-reading-404008:asia-south1:sensor"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
