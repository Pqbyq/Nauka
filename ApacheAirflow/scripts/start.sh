#!/bin/bash
# setup.sh - Skrypt ręcznej inicjalizacji Airflow

echo "====================================="
echo "  Inicjalizacja Apache Airflow"
echo "====================================="

# Sprawdzenie, czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker nie jest zainstalowany. Zainstaluj Docker przed kontynuowaniem."
    exit 1
fi

# Sprawdzenie, czy Docker Compose jest zainstalowany
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose nie jest zainstalowany. Zainstaluj Docker Compose przed kontynuowaniem."
    exit 1
fi

# Ustawienie AIRFLOW_UID dla systemów Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Ustawianie AIRFLOW_UID dla systemu Linux..."
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    echo "AIRFLOW_UID ustawiony na $(id -u)"
else
    # Dla Windows i innych systemów
    echo "AIRFLOW_UID=50000" > .env
    echo "AIRFLOW_UID ustawiony na 50000"
fi

# Tworzenie potrzebnych katalogów
echo "Tworzenie struktury katalogów..."
mkdir -p ./dags ./logs ./plugins ./data ./config

# Sprawdzenie czy plik config.py istnieje
if [ ! -f "./config/config.py" ]; then
    echo "Tworzenie podstawowego pliku konfiguracyjnego..."
    cat > ./config/config.py << 'EOF'
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
EOF
    echo "Plik config.py został utworzony. Pamiętaj, aby zastąpić 'YOUR_API_KEY' właściwym kluczem API."
fi

# Zatrzymanie istniejących kontenerów (jeśli istnieją)
echo "Zatrzymywanie istniejących kontenerów Airflow (jeśli istnieją)..."
docker-compose down

# Uruchomienie samej bazy danych
echo "Uruchamianie bazy danych PostgreSQL..."
docker-compose up -d postgres

echo "Czekanie na uruchomienie bazy danych..."
sleep 10

# Inicjalizacja bazy danych
echo "Inicjalizacja bazy danych Airflow..."
docker-compose run --rm airflow-webserver airflow db init

echo "Tworzenie użytkownika administratora..."
docker-compose run --rm airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Uruchomienie pozostałych usług
echo "Uruchamianie pozostałych usług Airflow..."
docker-compose up -d

echo "====================================="
echo "Apache Airflow został zainicjalizowany i uruchomiony!"
echo "Interfejs webowy dostępny pod adresem: http://localhost:8080"
echo "Dane logowania:"
echo "Użytkownik: admin"
echo "Hasło: admin"
echo "====================================="

echo "Czekanie na pełne uruchomienie wszystkich usług (może potrwać kilka minut)..."
sleep 30

echo "Sprawdzanie statusu kontenerów:"
docker-compose ps