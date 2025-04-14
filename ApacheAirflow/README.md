# Projekt Apache Airflow - System pobierania i analizy danych pogodowych

## Spis treści
1. [Opis projektu](#opis-projektu)
2. [Struktura projektu](#struktura-projektu)
3. [Wymagania systemowe](#wymagania-systemowe)
4. [Instalacja i konfiguracja](#instalacja-i-konfiguracja)
5. [Uruchomienie projektu](#uruchomienie-projektu)
6. [Logowanie do interfejsu Airflow](#logowanie-do-interfejsu-airflow)
7. [Weryfikacja działania](#weryfikacja-działania)
8. [Szczegółowy opis komponentów](#szczegółowy-opis-komponentów)
9. [Rozszerzanie projektu](#rozszerzanie-projektu)
10. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

## Opis projektu

Projekt przedstawia implementację potoku danych (data pipeline) przy użyciu Apache Airflow. System automatycznie pobiera dane pogodowe dla zdefiniowanych miast z API OpenWeatherMap, przetwarza je i zapisuje do plików CSV.

### Cel projektu

Głównym celem projektu jest demonstracja użycia Apache Airflow do orkiestracji zadań związanych z pobieraniem, przetwarzaniem i zapisywaniem danych. Projekt jest zorganizowany w sposób modułowy, co umożliwia jego łatwą rozbudowę i dostosowanie do innych źródeł danych lub formatów wyjściowych.

### Główne funkcjonalności

- Automatyczne pobieranie danych pogodowych dla wielu miast z API OpenWeatherMap
- Przetwarzanie danych (konwersja temperatury, kategoryzacja)
- Zapisywanie danych do plików CSV
- Harmonogramowanie zadań zgodnie z ustaloną częstotliwością
- Modułowa architektura ułatwiająca rozszerzanie funkcjonalności

## Struktura projektu

```
airflow-weather-project/
│
├── docker-compose.yml        # Konfiguracja Docker dla Airflow
├── .env                      # Zmienne środowiskowe
├── requirements.txt          # Dodatkowe zależności Pythona
│
├── dags/                     # Folder na DAGi Airflow
│   ├── weather_data_dag.py   # Główny DAG projektu
│   └── modules/              # Moduły projektu
│       ├── __init__.py       # Plik inicjalizacyjny pakietu modules
│       ├── extractors/       # Moduły do pobierania danych
│       │   ├── __init__.py   # Plik inicjalizacyjny pakietu extractors
│       │   └── weather_api.py # Moduł do pobierania danych z API pogodowego
│       ├── processors/       # Moduły do przetwarzania danych
│       │   ├── __init__.py   # Plik inicjalizacyjny pakietu processors
│       │   └── weather_processor.py # Moduł do przetwarzania danych pogodowych
│       ├── loaders/          # Moduły do zapisywania danych
│       │   ├── __init__.py   # Plik inicjalizacyjny pakietu loaders
│       │   └── csv_loader.py # Moduł do zapisywania danych do CSV
│       └── utils/            # Narzędzia pomocnicze
│           ├── __init__.py   # Plik inicjalizacyjny pakietu utils
│           └── logger.py     # Moduł do konfiguracji logowania
│
├── logs/                     # Logi Airflow (generowane automatycznie)
├── plugins/                  # Miejsce na własne pluginy Airflow
│
├── data/                     # Folder na dane wyjściowe
│   └── weather_data_*.csv    # Generowane pliki CSV z danymi
│
├── config/                   # Pliki konfiguracyjne
│   ├── __init__.py           # Plik inicjalizacyjny pakietu config
│   └── config.py             # Główny plik konfiguracyjny
│
├── scripts/                  # Pomocnicze skrypty
│   ├── start.sh              # Skrypt do uruchamiania środowiska
│   └── stop.sh               # Skrypt do zatrzymywania środowiska
│
└── README.md                 # Ten plik
```

## Wymagania systemowe

Przed rozpoczęciem instalacji upewnij się, że Twój system spełnia następujące wymagania:

- **Docker Engine**: wersja 20.10.0 lub nowsza
- **Docker Compose**: wersja 2.0.0 lub nowsza
- **Klucz API OpenWeatherMap**: darmowy klucz dostępny po rejestracji na [openweathermap.org](https://openweathermap.org/api)
- **Wolna przestrzeń dyskowa**: minimum 5 GB
- **RAM**: minimum 4 GB dostępne dla Docker

## Instalacja i konfiguracja

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/twoj-username/airflow-weather-project.git
cd airflow-weather-project
```

### 2. Konfiguracja klucza API

Edytuj plik `config/config.py` i zastąp wartość `YOUR_API_KEY` swoim kluczem API z OpenWeatherMap:

```python
# OpenWeatherMap API
API_KEY = "twoj_klucz_api"  # Zastąp swoim kluczem API
```

### 3. Tworzenie pliku .env

Na systemach Linux zaleca się ustawienie AIRFLOW_UID na identyfikator bieżącego użytkownika:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

Na systemach Windows lub macOS można utworzyć plik `.env` z zawartością:

```
AIRFLOW_UID=50000
```

### 4. Nadanie uprawnień do wykonywania skryptów

```bash
chmod +x scripts/start.sh scripts/stop.sh
```

## Uruchomienie projektu

### 1. Uruchomienie środowiska Airflow

```bash
./scripts/start.sh
```

Ten skrypt wykona następujące czynności:
- Sprawdzi wymagania wstępne (Docker, Docker Compose)
- Utworzy potrzebne katalogi
- Uruchomi kontenery Docker z Apache Airflow
- Zainicjalizuje bazę danych Airflow
- Utworzy użytkownika administratora

### 2. Sprawdzenie statusu kontenerów

```bash
docker-compose ps
```

Wszystkie kontenery powinny mieć status "Up" lub "Healthy".

### 3. Zatrzymanie środowiska

Gdy chcesz zatrzymać środowisko, użyj:

```bash
./scripts/stop.sh
```

## Logowanie do interfejsu Airflow

1. Otwórz przeglądarkę internetową i przejdź do adresu:
```
http://localhost:8080
```

2. Użyj następujących danych logowania:
   - **Użytkownik**: admin
   - **Hasło**: admin

3. Po zalogowaniu zobaczysz listę dostępnych DAG-ów, w tym `weather_data_pipeline`.

## Weryfikacja działania

### 1. Aktywacja DAG

1. W interfejsie webowym Airflow znajdź DAG o nazwie `weather_data_pipeline`.
2. Włącz DAG, przełączając przycisk po lewej stronie nazwy na pozycję "On".
3. Kliknij przycisk "Trigger DAG" (trójkąt po prawej stronie), aby ręcznie uruchomić DAG.

### 2. Monitorowanie wykonania

1. Kliknij na nazwę DAG, aby zobaczyć szczegóły.
2. Przejdź do zakładki "Graph View", aby zobaczyć wizualizację zadań.
3. Monitoruj status zadań - wszystkie powinny zmienić kolor na zielony po zakończeniu.

### 3. Sprawdzenie wyników

Po pomyślnym wykonaniu DAG, dane pogodowe zostaną zapisane w plikach CSV w katalogu `data`. Możesz sprawdzić wyniki na kilka sposobów:

#### Bezpośrednio z systemu plików hosta:

```bash
# Lista plików w katalogu data
ls -la ./data

# Podgląd zawartości pliku CSV
head -n 10 ./data/weather_data_*.csv
```

#### Poprzez kontener Docker:

```bash
# Sprawdzenie plików wewnątrz kontenera
docker-compose exec airflow-webserver ls -la /opt/airflow/data

# Podgląd zawartości pliku CSV wewnątrz kontenera
docker-compose exec airflow-webserver head -n 10 /opt/airflow/data/weather_data_*.csv
```

#### Poprzez logi w interfejsie Airflow:

1. W szczegółach DAG, kliknij na zadanie `save_to_csv`.
2. Wybierz zakładkę "Logs".
3. Znajdź komunikat "Zapisano dane do pliku: /opt/airflow/data/weather_data_*.csv".

## Szczegółowy opis komponentów

### Pliki konfiguracyjne

#### `config/config.py`

Centralny plik konfiguracyjny zawierający:

```python
# OpenWeatherMap API
API_KEY = "YOUR_API_KEY"  # Klucz API do OpenWeatherMap
CITIES = ["Warsaw", "Berlin", "Paris", "London", "Madrid"]  # Lista miast do monitorowania

# Ścieżki
DATA_FOLDER = "/opt/airflow/data"  # Ścieżka do folderu z danymi

# Konfiguracja logowania
LOG_LEVEL = "INFO"  # Poziom logowania

# Harmonogram domyślny (co godzinę)
DEFAULT_SCHEDULE_INTERVAL = "@hourly"  # Częstotliwość uruchamiania DAG
```

### DAG główny

#### `dags/weather_data_dag.py`

Główny plik definiujący przepływ pracy (DAG - Directed Acyclic Graph):

**Kluczowe elementy:**
- Import modułów projektu
- Definicja domyślnych argumentów DAG (retry, scheduling)
- Definicja DAG z harmonogramem
- Definicja zadań z użyciem PythonOperator
- Ustawienie zależności między zadaniami

### Moduły projektu

#### `dags/modules/extractors/weather_api.py`

Moduł odpowiedzialny za pobieranie danych z API pogodowego.

**Kluczowe funkcje:**
- `fetch_weather_for_city(city)`: Pobiera dane pogodowe dla pojedynczego miasta
- `fetch_weather_data(**kwargs)`: Pobiera dane dla wszystkich miast z konfiguracji

#### `dags/modules/processors/weather_processor.py`

Moduł do przetwarzania i transformacji danych pogodowych.

**Kluczowe funkcje:**
- `categorize_temperature(temp)`: Kategoryzuje temperaturę (cold, moderate, warm)
- `celsius_to_fahrenheit(celsius)`: Konwertuje temperaturę z Celsjusza na Fahrenheita
- `enrich_weather_data(weather_item)`: Wzbogaca pojedynczy element danych
- `process_weather_data(**kwargs)`: Przetwarza wszystkie pobrane dane

#### `dags/modules/loaders/csv_loader.py`

Moduł do zapisywania danych do plików CSV.

**Kluczowe funkcje:**
- `save_to_csv(**kwargs)`: Zapisuje przetworzone dane do pliku CSV

#### `dags/modules/utils/logger.py`

Moduł do konfiguracji logowania.

**Kluczowe funkcje:**
- `setup_logger(name)`: Konfiguruje i zwraca logger dla danego modułu

### Skrypty pomocnicze

#### `scripts/start.sh`

Skrypt do uruchamiania środowiska Airflow:
- Sprawdza wymagania wstępne
- Tworzy potrzebne katalogi
- Ustawia zmienne środowiskowe
- Uruchamia kontenery Docker

#### `scripts/stop.sh`

Skrypt do zatrzymywania środowiska Airflow:
- Zatrzymuje wszystkie kontenery
- Wyświetla informacje o czyszczeniu środowiska

## Rozszerzanie projektu

Projekt został zaprojektowany w sposób modułowy, dzięki czemu można go łatwo rozszerzać. Oto kilka pomysłów na rozszerzenie:

### 1. Dodanie nowych źródeł danych

Aby dodać nowe źródło danych:
1. Utwórz nowy plik w katalogu `dags/modules/extractors/`
2. Zaimplementuj funkcję do pobierania danych
3. Dodaj nowe zadanie w pliku DAG

### 2. Dodanie zaawansowanego przetwarzania

Aby dodać bardziej zaawansowane przetwarzanie:
1. Utwórz nowy plik w katalogu `dags/modules/processors/`
2. Zaimplementuj funkcje przetwarzania
3. Dodaj nowe zadanie w pliku DAG

### 3. Dodanie nowych formatów wyjściowych

Aby dodać nowy format wyjściowy (np. JSON, baza danych):
1. Utwórz nowy plik w katalogu `dags/modules/loaders/`
2. Zaimplementuj funkcję do zapisywania danych
3. Dodaj nowe zadanie w pliku DAG

## Rozwiązywanie problemów

### 1. Problemy z inicjalizacją bazy danych

**Problem**: Komunikat "You need to initialize the database"

**Rozwiązanie**:
```bash
# Zatrzymaj kontenery
docker-compose down

# Uruchom inicjalizację bazy danych ręcznie
docker-compose run --rm airflow-webserver airflow db init

# Uruchom ponownie kontenery
docker-compose up -d
```

### 2. Problemy z importami modułów

**Problem**: Błędy typu "ModuleNotFoundError"

**Rozwiązanie**:
Upewnij się, że wszystkie pliki `__init__.py` istnieją w odpowiednich katalogach i że ścieżki importów są poprawnie skonfigurowane.

### 3. Problemy z API OpenWeatherMap

**Problem**: Błędy związane z API

**Rozwiązanie**:
- Sprawdź, czy Twój klucz API jest poprawny
- Sprawdź, czy nazwy miast są poprawnie zapisane
- Sprawdź, czy nie przekroczyłeś limitu zapytań dla darmowego klucza API

### 4. Problemy z uprawnieniami do plików

**Problem**: Błędy związane z uprawnieniami do plików

**Rozwiązanie**:
```bash
# Ustaw właściwy AIRFLOW_UID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Zatrzymaj i uruchom ponownie kontenery
docker-compose down
docker-compose up -d
```