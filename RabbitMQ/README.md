# Platforma Komunikacji RabbitMQ

![Logo RabbitMQ](https://www.rabbitmq.com/img/logo-rabbitmq.svg)

## 📋 Przegląd projektu

Kompleksowe rozwiązanie do wdrożenia i konfiguracji brokera wiadomości RabbitMQ wraz z narzędziami do monitorowania i aplikacją demonstracyjną. Projekt zapewnia kompletną infrastrukturę gotową do użycia w środowiskach testowych i produkcyjnych.

[![Licencja: MIT](https://img.shields.io/badge/Licencja-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Funkcje

- **Broker RabbitMQ** z zaawansowaną konfiguracją i panelem zarządzania
- **Trwałe kolejki** odporne na awarie i restarty
- **Monitoring** oparty na Prometheus i Grafana
- **Przykładowa aplikacja Python** demonstrująca wzorce wymiany wiadomości:
  - Direct Exchange (zadania)
  - Fanout Exchange (powiadomienia)
- **Elastyczna konfiguracja** za pomocą zmiennych środowiskowych
- **Skalowalność** dzięki architekturze opartej na kontenerach
- **Bezpieczeństwo** z odpowiednią konfiguracją użytkowników i uprawnień

## 🛠️ Technologie

- Docker i Docker Compose
- RabbitMQ 3.10 z wtyczkami zarządzania
- Python 3.9
- Pika (klient RabbitMQ dla Pythona)
- Prometheus (monitoring)
- Grafana (wizualizacja metryk)

## 📂 Struktura projektu

```
.
├── app/                         # Aplikacja Python
│   ├── consumer.py              # Konsument wiadomości
│   ├── producer.py              # Producent wiadomości
│   ├── requirements.txt         # Zależności Pythona
│   └── Dockerfile               # Definicja obrazu aplikacji
│
├── rabbitmq/                    # Konfiguracja RabbitMQ
│   ├── rabbitmq.conf            # Główny plik konfiguracyjny
│   ├── definitions.json         # Definicje użytkowników, kolejek i wymian
│   └── enabled_plugins          # Włączone wtyczki RabbitMQ
│
├── prometheus/                  # Konfiguracja Prometheus
│   └── prometheus.yml           # Konfiguracja zbierania metryk
│
├── docker-compose.yml           # Kompozycja kontenerów Docker
└── Makefile                     # Pomocnicze polecenia do zarządzania
```

## 📁 Opisy plików i kluczowe zmienne

### Plik Docker Compose
**Ścieżka**: `docker-compose.yml`

Ten plik orkiestruje wszystkie kontenery potrzebne dla platformy.

**Kluczowe komponenty**:
- **Usługa rabbitmq**: Główny broker wiadomości
  - `image: rabbitmq:3.10-management` - Używa RabbitMQ 3.10 z interfejsem zarządzania
  - `RABBITMQ_DEFAULT_USER=admin` - Domyślna nazwa użytkownika administratora
  - `RABBITMQ_DEFAULT_PASS=admin_password` - Domyślne hasło administratora
  - `RABBITMQ_ERLANG_COOKIE=SWQOKODSQALRPCLNMEQG` - Token uwierzytelniania dla węzłów klastra
  - Porty: 5672 (AMQP), 15672 (Interfejs zarządzania), 1883 (MQTT), 15675 (WebSockets)
  - Woluminy: Mapuje pliki konfiguracyjne i przechowuje dane

- **Usługa prometheus**: Zbieranie metryk
  - `image: prom/prometheus` - Oficjalny obraz Prometheus
  - Port 9090 - Interfejs webowy
  - Zamontowany plik konfiguracyjny jako wolumin

- **Usługa grafana**: Wizualizacja metryk
  - `image: grafana/grafana` - Oficjalny obraz Grafana
  - Port 3000 - Interfejs webowy
  - Trwały wolumin dla danych dashboardów

- **Usługa consumer**: Usługa przetwarzania wiadomości
  - Zbudowana z Dockerfile aplikacji
  - Automatycznie uruchamiana ze stosem
  - Zmienna środowiskowa `RABBITMQ_HOST=rabbitmq-broker` do wykrywania usług

- **Usługa producer**: Generator wiadomości
  - Zbudowana z Dockerfile aplikacji
  - Uruchamiana jednorazowo w celu wygenerowania przykładowych wiadomości
  - Zależna od gotowości konsumenta

### Konfiguracja RabbitMQ
**Ścieżka**: `rabbitmq/rabbitmq.conf`

Główny plik konfiguracyjny brokera.

**Kluczowe ustawienia**:
- `vm_memory_high_watermark.relative = 0.7` - Próg pamięci (70% pamięci systemowej)
- `disk_free_limit.relative = 2.0` - Próg miejsca na dysku (2x rozmiar pamięci)
- `loopback_users = none` - Zezwalaj na połączenia spoza localhost
- `listeners.tcp.default = 5672` - Główny port AMQP
- `management.tcp.port = 15672` - Port interfejsu zarządzania
- `heartbeat = 60` - Interwał pulsu połączenia (w sekundach)
- `channel_max = 2000` - Maksymalna liczba kanałów na połączenie
- `connection_max = 1000` - Maksymalna liczba jednoczesnych połączeń

### Definicje RabbitMQ
**Ścieżka**: `rabbitmq/definitions.json`

Automatyczna konfiguracja użytkowników, hostów wirtualnych, wymian, kolejek i powiązań.

**Kluczowe komponenty**:
- **Użytkownicy**:
  - `admin` - Administrator z pełnym dostępem
  - `app_user` - Użytkownik aplikacji z tagiem monitorowania

- **Hosty wirtualne**:
  - `/` - Domyślny host wirtualny
  - `my_app_vhost` - Dedykowany host wirtualny aplikacji

- **Uprawnienia**:
  - Mapowane uprawnienia między użytkownikami a hostami wirtualnymi
  - Definiowane uprawnienia konfiguracji, odczytu i zapisu za pomocą wzorców regex

- **Kolejki**:
  - `task_queue` - Trwała klasyczna kolejka dla zadań z parametrami:
    - `x-queue-type: classic`
    - `x-max-length: 10000` - Maksymalna liczba wiadomości
    - `x-message-ttl: 3600000` - Czas życia (1 godzina)
  
  - `notification_queue` - Trwała kolejka quorum dla powiadomień z parametrami:
    - `x-queue-type: quorum` - Typ kolejki o wysokiej dostępności
    - `x-max-length: 10000` - Maksymalna liczba wiadomości
    - `x-message-ttl: 86400000` - Czas życia (24 godziny)

- **Wymiany**:
  - `task_exchange` - Wymiana typu direct dla określonego routingu
  - `notification_exchange` - Wymiana typu fanout do rozgłaszania

- **Powiązania**:
  - Mapuje `task_exchange` do `task_queue` z kluczem routingu `task`
  - Mapuje `notification_exchange` do `notification_queue` (bez konkretnego klucza routingu)

### Wtyczki RabbitMQ
**Ścieżka**: `rabbitmq/enabled_plugins`

Lista włączonych wtyczek dla rozszerzonej funkcjonalności.

**Kluczowe wtyczki**:
- `rabbitmq_management` - Webowy interfejs użytkownika i monitoring
- `rabbitmq_prometheus` - Eksportuje metryki do Prometheusa
- `rabbitmq_mqtt` - Obsługa protokołu MQTT
- `rabbitmq_web_mqtt` - MQTT przez WebSockets
- `rabbitmq_shovel` - Transfer wiadomości między węzłami
- `rabbitmq_federation` - Federacja brokerów dla konfiguracji rozproszonych
- `rabbitmq_shovel_management` - Interfejs zarządzania shovelem
- `rabbitmq_federation_management` - Interfejs zarządzania federacją

### Konfiguracja Prometheus
**Ścieżka**: `prometheus/prometheus.yml`

Konfiguracja zbierania metryk.

**Kluczowe ustawienia**:
- `scrape_interval: 15s` - Jak często zbierać metryki
- `evaluation_interval: 15s` - Jak często oceniać reguły
- `targets: ['rabbitmq-broker:15692']` - Endpoint metryk RabbitMQ
- `metrics_path: '/metrics'` - Ścieżka URL metryk

### Producent Python
**Ścieżka**: `app/producer.py`

Komponent generujący wiadomości.

**Kluczowe funkcje i zmienne**:
- **Ustawienia połączenia**:
  - `RABBITMQ_HOST = 'localhost'` - Nazwa hosta (zmienia się na 'rabbitmq-broker' w Dockerze)
  - `RABBITMQ_PORT = 5672` - Domyślny port AMQP
  - `RABBITMQ_VHOST = 'my_app_vhost'` - Host wirtualny dla aplikacji
  - `RABBITMQ_USER = 'app_user'` - Nazwa użytkownika aplikacji
  - `RABBITMQ_PASS = 'app_password'` - Hasło aplikacji

- **Ustawienia wymiany i routingu**:
  - `TASK_EXCHANGE = 'task_exchange'` - Nazwa wymiany dla zadań
  - `TASK_ROUTING_KEY = 'task'` - Klucz routingu dla zadań
  - `NOTIFICATION_EXCHANGE = 'notification_exchange'` - Wymiana dla powiadomień

- **Funkcje**:
  - `connect_to_rabbitmq()` - Nawiązuje połączenie z logiką ponawiania
  - `publish_task_message()` - Publikuje zadania z priorytetami i potwierdza dostarczenie
  - `publish_notification()` - Rozgłasza powiadomienia do wszystkich subskrybentów
  - `main()` - Funkcja demonstracyjna, która publikuje przykładowe wiadomości

- **Struktura wiadomości**:
  - Wiadomości zadań zawierają task_id, task_type, priority, timestamp i data
  - Wiadomości powiadomień zawierają notification_id, type, subject, content i timestamp

### Konsument Python
**Ścieżka**: `app/consumer.py`

Komponent przetwarzający wiadomości.

**Kluczowe funkcje i zmienne**:
- **Ustawienia połączenia**: Takie same jak dla producenta

- **Nazwy kolejek**:
  - `TASK_QUEUE = 'task_queue'` - Kolejka do przetwarzania zadań
  - `NOTIFICATION_QUEUE = 'notification_queue'` - Kolejka do odbierania powiadomień

- **Funkcje**:
  - `connect_to_rabbitmq()` - Nawiązuje połączenie z logiką ponawiania
  - `process_task()` - Symuluje przetwarzanie zadań z czasem opartym na priorytecie
  - `process_notification()` - Obsługuje wiadomości powiadomień
  - `task_callback()` - Funkcja callback dla wiadomości z kolejki zadań
  - `notification_callback()` - Funkcja callback dla wiadomości powiadomień
  - `start_consumer()` - Uruchamia konsumenta dla określonej kolejki
  - `main()` - Uruchamia oba konsumenty w osobnych wątkach

- **Logika przetwarzania**:
  - Używa basic_qos z prefetch_count=1 dla sprawiedliwego rozdzielania
  - Implementuje wzorce potwierdzania (ack/nack)
  - Obsługuje ponowne umieszczanie w kolejce dla nieudanego przetwarzania zadań
  - Używa wątków do równoległego przetwarzania różnych typów kolejek

### Wymagania Python
**Ścieżka**: `app/requirements.txt`

Zależności Pythona:
- `pika==1.3.1` - Biblioteka klienta RabbitMQ
- `python-dotenv==1.0.0` - Zarządzanie zmiennymi środowiskowymi

### Dockerfile aplikacji
**Ścieżka**: `app/Dockerfile`

Definicja kontenera dla aplikacji Python:
- Używa obrazu bazowego Python 3.9 slim
- Instaluje wymagane zależności
- Konfiguruje katalog aplikacji
- Czyni skrypty wykonywalnymi
- Konfiguruje niebuforowane wyjście Pythona
- Polecenie jest określone w docker-compose.yml

### Makefile
**Ścieżka**: `Makefile`

Skrypt pomocniczy z predefiniowanymi poleceniami do zarządzania platformą:
- `setup` - Tworzy niezbędne katalogi
- `deploy-infra` - Wdraża RabbitMQ i monitoring
- `deploy-app` - Wdraża aplikację konsumenta
- `logs` - Pokazuje logi RabbitMQ
- `run-producer` - Uruchamia producenta w celu generowania wiadomości
- `restart` - Restartuje wszystkie kontenery
- `status` - Pokazuje status kontenerów
- `stop` - Zatrzymuje wszystkie kontenery
- `clean` - Usuwa wszystkie kontenery i woluminy

## 🔧 Instalacja i uruchomienie

### Wymagania wstępne

- Docker i Docker Compose
- Make (opcjonalnie, upraszcza zarządzanie)
- Git

### Klonowanie repozytorium

```bash
git clone https://github.com/twoja-nazwa-uzytkownika/rabbitmq-platform.git
cd rabbitmq-platform
```

### Początkowa konfiguracja

1. Utworzenie struktury katalogów:

```bash
make setup
```

lub ręcznie:

```bash
mkdir -p rabbitmq prometheus grafana app
```

2. Uruchomienie infrastruktury:

```bash
make deploy-infra
```

lub za pomocą Docker Compose:

```bash
docker-compose up -d rabbitmq prometheus grafana
```

3. Uruchomienie aplikacji konsumenta:

```bash
make deploy-app
```

lub bezpośrednio:

```bash
docker-compose up -d consumer
```

4. Generowanie przykładowych wiadomości:

```bash
make run-producer
```

lub:

```bash
docker-compose up producer
```

### Dla użytkowników Windows

Jeśli używasz systemu Windows, gdzie polecenie `make` nie jest dostępne, możesz bezpośrednio używać poleceń Docker Compose:

```powershell
# Zamiast make setup
mkdir -p rabbitmq prometheus grafana app

# Zamiast make deploy-infra
docker-compose up -d rabbitmq prometheus grafana

# Zamiast make deploy-app
docker-compose up -d consumer

# Zamiast make run-producer
docker-compose up producer

# Zamiast make logs
docker-compose logs -f rabbitmq

# Zamiast make status
docker-compose ps

# Zamiast make stop
docker-compose stop

# Zamiast make clean
docker-compose down -v
```

### Dostęp do interfejsów

- **Panel zarządzania RabbitMQ**: http://localhost:15672
  - Login: `admin`
  - Hasło: `admin_password`

- **Prometheus**: http://localhost:9090

- **Grafana**: http://localhost:3000
  - Login: `admin`
  - Hasło: `admin` (przy pierwszym logowaniu)

## 📊 Monitoring

### Prometheus

Zbiera metryki z RabbitMQ, takie jak:
- Liczba wiadomości w kolejkach
- Szybkość publikowania/konsumpcji
- Wykorzystanie zasobów (RAM, CPU, dysk)
- Statystyki połączeń

### Grafana

Do konfigurowania dashboardów wizualizujących:
- Przepustowość systemu
- Opóźnienia w przetwarzaniu wiadomości
- Alerty o przeciążeniu kolejek
- Stan zdrowia brokera

## 🔍 Weryfikacja poprawności działania

### Sprawdzanie statusu kontenerów

Zanim przejdziesz do weryfikacji RabbitMQ, upewnij się, że wszystkie kontenery są uruchomione:

```bash
docker-compose ps
```

Wszystkie kontenery powinny mieć status "Up". W szczególności sprawdź, czy kontener `rabbitmq-broker` jest aktywny.

### Dostęp do interfejsu zarządzania RabbitMQ

#### Logowanie do panelu administracyjnego

1. Otwórz przeglądarkę internetową
2. Przejdź do adresu: http://localhost:15672
3. Zaloguj się używając następujących danych:
   - Login: `admin`
   - Hasło: `admin_password`

#### Przeglądanie ogólnego statusu systemu

Po zalogowaniu zobaczysz stronę przeglądu, która zawiera:

1. **Zakładka Overview** - pokazuje podstawowe statystyki i zdrowie systemu
   - Sprawdź, czy status węzła jest `running`
   - Zwróć uwagę na grafy pokazujące ruch wiadomości, które powinny pokazywać aktywność po uruchomieniu producenta

2. **Informacje o wersji i systemie**
   - Wersja RabbitMQ powinna być zgodna z zainstalowaną (3.10.x)
   - Sprawdź, czy wszystkie wtyczki są prawidłowo załadowane (powinny być wymienione w dolnej części strony)

### Weryfikacja kolejek i wiadomości

#### Sprawdzanie stanu kolejek

1. Kliknij zakładkę **Queues** w górnym menu
2. Powinieneś zobaczyć dwie kolejki:
   - `task_queue` - w hoście wirtualnym `my_app_vhost`
   - `notification_queue` - w hoście wirtualnym `my_app_vhost`

3. Dla każdej kolejki sprawdź:
   - Status (powinna być aktywna)
   - Liczba gotowych wiadomości (Ready) - może się zmieniać
   - Liczba niezatwierdzonych wiadomości (Unacked) - powinna być niska lub zerowa, jeśli konsument działa poprawnie

#### Przeglądanie wiadomości w kolejkach

Aby zobaczyć wiadomości znajdujące się w kolejce:

1. Kliknij nazwę kolejki (np. `task_queue`)
2. Przejdź do zakładki **Get messages**
3. Ustaw parametry:
   - **Acknowledgement mode**: `Automatic ack` (do celów testowych)
   - **Encoding**: `Auto` lub `String`
   - **Message count**: Liczba wiadomości do pobierania (np. `5`)
4. Kliknij przycisk **Get Message(s)**

Teraz powinieneś zobaczyć zawartość wiadomości w formacie JSON. Przykładowa wiadomość z kolejki zadań może wyglądać tak:

```json
{
  "task_id": 1,
  "task_type": "process",
  "priority": 7,
  "timestamp": "2025-04-13T12:34:56.789Z",
  "data": {
    "value": 42,
    "description": "Task data for task 1"
  }
}
```

#### Publikowanie testowych wiadomości

Aby przetestować system, możesz ręcznie opublikować wiadomość:

1. Przejdź do zakładki **Exchanges** w górnym menu
2. Kliknij na nazwę wymiany (np. `task_exchange` w hoście `my_app_vhost`)
3. Przewiń w dół do sekcji **Publish message**
4. Wypełnij pola:
   - **Routing key**: `task` (dla task_exchange)
   - **Properties**: Możesz dodać opcjonalne właściwości, jak `content_type = application/json`
   - **Payload**: Wprowadź wiadomość JSON, np.:
     ```json
     {
       "task_id": 999,
       "task_type": "manual_test",
       "priority": 10,
       "timestamp": "2025-04-13T15:00:00.000Z",
       "data": {
         "value": 100,
         "description": "Manually published test task"
       }
     }
     ```
5. Kliknij przycisk **Publish message**

Następnie sprawdź logi konsumenta, aby zobaczyć, czy wiadomość została przetworzona:

```bash
docker-compose logs -f consumer
```

### Weryfikacja połączeń i kanałów

Aby sprawdzić aktywne połączenia:

1. Kliknij zakładkę **Connections** w górnym menu
2. Powinieneś zobaczyć co najmniej jedno połączenie od konsumenta
3. Kliknij na połączenie, aby zobaczyć szczegóły, w tym:
   - Adres IP klienta
   - Informacje o kanałach
   - Statystyki przepustowości

Aby sprawdzić kanały:

1. Kliknij zakładkę **Channels** w górnym menu
2. Zobaczysz listę aktywnych kanałów, wraz z informacjami o konsumpcji i statusie prefetch
3. Kliknij na kanał, aby zobaczyć szczegóły konsumpcji i bindingów

### Monitorowanie systemu

#### Prometheus

Aby zweryfikować zbieranie metryk:

1. Otwórz przeglądarkę i przejdź do adresu: http://localhost:9090
2. Przejdź do zakładki **Status** -> **Targets**
3. Sprawdź, czy cel `rabbitmq` ma status `UP`

Aby sprawdzić konkretne metryki:

1. Wróć do strony głównej Prometheusa
2. W polu zapytania wpisz jedną z poniższych metryk i kliknij **Execute**:
   - `rabbitmq_queue_messages` - liczba wiadomości we wszystkich kolejkach
   - `rabbitmq_connections` - liczba aktywnych połączeń
   - `rabbitmq_consumers` - liczba konsumentów

3. Przełącz się na widok wykresu (**Graph**), aby zobaczyć zmianę metryk w czasie

#### Grafana

Aby skonfigurować dashboard dla RabbitMQ w Grafana:

1. Otwórz przeglądarkę i przejdź do adresu: http://localhost:3000
2. Zaloguj się domyślnymi danymi (admin/admin) i ustaw nowe hasło jeśli to pierwszy login
3. Przejdź do **Configuration** -> **Data sources**
4. Kliknij **Add data source**
5. Wybierz **Prometheus**
6. W polu URL wpisz `http://prometheus:9090`
7. Kliknij **Save & Test** - powinieneś zobaczyć komunikat o sukcesie

Następnie zaimportuj dashboard RabbitMQ:

1. Przejdź do zakładki **Dashboards** -> **Import**
2. Wpisz ID: `10991` (oficjalny dashboard RabbitMQ)
3. Kliknij **Load**
4. Wybierz swojego źródła danych Prometheus
5. Kliknij **Import**

Teraz powinieneś zobaczyć dashboard z metrykami RabbitMQ, w tym:
- Stan kolejek
- Ruch wiadomości
- Wykorzystanie zasobów
- Metryki wydajności

### Diagnostyka typowych problemów

#### Problem: Kontener RabbitMQ nie uruchamia się

**Sprawdzenie:**
```bash
docker-compose logs rabbitmq
```

**Rozwiązanie:**
- Sprawdź, czy porty nie są zajęte przez inne aplikacje (5672, 15672)
- Upewnij się, że pliki konfiguracyjne są poprawnie zamontowane
- Sprawdź uprawnienia do woluminów

#### Problem: Aplikacja nie może połączyć się z RabbitMQ

**Sprawdzenie:**
```bash
docker-compose logs consumer
```

**Rozwiązanie:**
- Upewnij się, że używasz poprawnej nazwy hosta (`rabbitmq-broker` w sieci Docker)
- Sprawdź, czy poświadczenia są poprawne
- Sprawdź, czy host wirtualny istnieje i użytkownik ma do niego dostęp

#### Problem: Wiadomości nie są konsumowane

**Sprawdzenie:**
1. Sprawdź liczbę wiadomości w kolejce w interfejsie zarządzania
2. Sprawdź logi konsumenta:
```bash
docker-compose logs consumer
```

**Rozwiązanie:**
- Upewnij się, że konsument jest uruchomiony
- Sprawdź, czy konsument ma odpowiednie uprawnienia
- Sprawdź, czy bindingi między wymianami a kolejkami są poprawne

### Testy działania aplikacji demonstracyjnej

#### Test producenta

1. Uruchom producenta, aby wygenerować wiadomości:
```bash
docker-compose up producer
```

2. Sprawdź logi, aby upewnić się, że wiadomości zostały opublikowane:
```bash
docker-compose logs producer
```

Powinieneś zobaczyć komunikaty o opublikowanych zadaniach i powiadomieniach.

#### Test konsumenta

1. Sprawdź logi konsumenta, aby upewnić się, że wiadomości są odbierane:
```bash
docker-compose logs consumer
```

Powinieneś zobaczyć komunikaty o odebranych zadaniach i powiadomieniach oraz o ich przetwarzaniu.

#### Test pełnego obiegu wiadomości

1. Upewnij się, że konsument jest uruchomiony:
```bash
docker-compose up -d consumer
```

2. Uruchom producenta w trybie jednorazowym:
```bash
docker-compose up producer
```

3. Sprawdź logi obu komponentów:
```bash
docker-compose logs --tail=50 producer consumer
```

Powinieneś zobaczyć pełny obieg wiadomości - od publikacji przez producenta do przetworzenia przez konsumenta.

4. Sprawdź w interfejsie zarządzania RabbitMQ, czy wszystkie wiadomości zostały przetworzone (liczba wiadomości w statusie "Ready" powinna być niska lub zerowa).

## 🚦 Zarządzanie platformą

Projekt zawiera Makefile z pomocnymi poleceniami:

```
make help          - Wyświetla dostępne polecenia
make setup         - Tworzy niezbędne katalogi
make deploy-infra  - Uruchamia RabbitMQ, Prometheus i Grafana
make deploy-app    - Uruchamia aplikację konsumenta
make logs          - Pokazuje logi z kontenera RabbitMQ
make run-producer  - Uruchamia producenta do generowania wiadomości
make restart       - Restartuje wszystkie kontenery
make status        - Pokazuje status wszystkich kontenerów
make stop          - Zatrzymuje wszystkie kontenery
make clean         - Usuwa wszystkie kontenery i woluminy
```

## 📈 Skalowanie

### Skalowanie poziome (Konsumenci)

```bash
# Uruchomienie wielu instancji konsumenta
docker-compose up -d --scale consumer=3
```

### Skalowanie pionowe (Zasoby)

Edytuj plik `docker-compose.yml` i dodaj limity zasobów:

```yaml
services:
  rabbitmq:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## 🔐 Bezpieczeństwo

### Zmiana domyślnych haseł

Edytuj plik `rabbitmq/definitions.json` i zmień hasła dla użytkowników. Hasła są w formacie hash SHA256.

### Włączenie SSL/TLS

Dodaj następującą konfigurację do `rabbitmq.conf`:

```
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
ssl_options.cacertfile = /path/to/ca_certificate.pem
ssl_options.certfile = /path/to/server_certificate.pem
ssl_options.keyfile = /path/to/server_key.pem
```

## 🌎 Zastosowanie produkcyjne

Przed wdrożeniem w środowisku produkcyjnym rozważ:

1. **Klastrowanie** dla wysokiej dostępności
2. **Kopie zapasowe** definicji i konfiguracji
3. **Rotację logów**
4. **Monitoring i alarmowanie**
5. **Zarządzanie hasłami** (Vault/Secret Manager)
6. **Konteneryzację** (Kubernetes zamiast Docker Compose)

## 📚 Dodatkowe zasoby

- [Oficjalna dokumentacja RabbitMQ](https://www.rabbitmq.com/documentation.html)
- [Dokumentacja Pika](https://pika.readthedocs.io/)
- [Dokumentacja Prometheus](https://prometheus.io/docs/)
- [Dokumentacja Grafana](https://grafana.com/docs/)

## 🤝 Współpraca

Zapraszamy do współpracy! Jeśli masz pomysły na ulepszenie projektu:

1. Zrób fork repozytorium
2. Utwórz branch ze swoją funkcjonalnością
3. Wyślij pull request

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik `LICENSE` dla szczegółów.

## ✨ Autor

[pqbq]

---

*Projekt został stworzony jako demonstracja architektury komunikacji z użyciem RabbitMQ i kontenerów Docker.*