"""
Plik konfiguracyjny dla projektu Airflow
"""

# OpenWeatherMap API
API_KEY = "0d05be65b828fe95f3be9a4700122799"  # Zastąp swoim kluczem API
CITIES = ["Warsaw", "Berlin", "Paris", "London", "Madrid"]

# Ścieżki
DATA_FOLDER = "/opt/airflow/data"

# Konfiguracja logowania
LOG_LEVEL = "INFO"

# Harmonogram domyślny (co godzinę)
DEFAULT_SCHEDULE_INTERVAL = "@hourly"
