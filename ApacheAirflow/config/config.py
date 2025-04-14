"""
Plik konfiguracyjny dla projektu Airflow
"""
import os

# OpenWeatherMap API
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")  # klucz z pliku .env (patrz .env.example)
CITIES = ["Warsaw", "Berlin", "Paris", "London", "Madrid"]

# Ścieżki
DATA_FOLDER = "/opt/airflow/data"

# Konfiguracja logowania
LOG_LEVEL = "INFO"

# Harmonogram domyślny (co godzinę)
DEFAULT_SCHEDULE_INTERVAL = "@hourly"
