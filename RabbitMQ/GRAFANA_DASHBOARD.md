# Konfiguracja dashboardów RabbitMQ w Grafanie

Ten przewodnik zawiera szczegółowe instrukcje dotyczące konfiguracji dashboardów w Grafanie do monitorowania kolejek RabbitMQ. Opisuje zarówno sposób importowania gotowych dashboardów, jak i tworzenie własnych, dostosowanych do specyficznych potrzeb.

## Spis treści
- [Wymagania wstępne](#wymagania-wstępne)
- [Konfiguracja źródła danych Prometheus](#konfiguracja-źródła-danych-prometheus)
- [Importowanie gotowych dashboardów](#importowanie-gotowych-dashboardów)
- [Tworzenie własnego dashboardu RabbitMQ](#tworzenie-własnego-dashboardu-rabbitmq)
- [Przydatne metryki do monitorowania kolejek](#przydatne-metryki-do-monitorowania-kolejek)
- [Konfiguracja alertów](#konfiguracja-alertów)
- [Rozwiązywanie problemów z dashboardami](#rozwiązywanie-problemów-z-dashboardami)

## Wymagania wstępne

Przed rozpoczęciem konfiguracji dashboardów upewnij się, że:

1. RabbitMQ jest uruchomiony z włączoną wtyczką `rabbitmq_prometheus`
2. Prometheus jest skonfigurowany do zbierania metryk z RabbitMQ (port 15692)
3. Grafana jest zainstalowana i działa (domyślnie na porcie 3000)
4. Masz uprawnienia administratora w Grafanie

## Konfiguracja źródła danych Prometheus

Zanim zaimportujesz lub utworzysz dashboard, musisz skonfigurować Prometheus jako źródło danych w Grafanie:

1. Otwórz przeglądarkę i przejdź do adresu Grafany: http://localhost:3000
2. Zaloguj się jako admin (domyślne dane: admin/admin)
3. W menu bocznym, przejdź do **Configuration** (ikona koła zębatego) → **Data sources**
4. Kliknij przycisk **Add data source**
5. Wybierz **Prometheus**
6. Wypełnij formularz:
   - Name: `Prometheus` (lub inna nazwa)
   - URL: `http://prometheus:9090` (nazwa serwisu z docker-compose.yml, NIE używaj localhost)
   - Access: `Server (default)`
   - Pozostałe ustawienia pozostaw domyślne
7. Na dole strony kliknij **Save & Test**
8. Powinieneś zobaczyć zielony komunikat "Data source is working"

> **WAŻNE**: W środowisku Docker musisz używać nazwy usługi (`prometheus`) zamiast `localhost`. Każdy kontener ma własną przestrzeń sieciową i `localhost` w kontenerze Grafana odnosi się do samej Grafany, a nie do hosta lub innych kontenerów.

## Importowanie gotowych dashboardów

### Importowanie oficjalnego dashboardu RabbitMQ

1. W Grafanie, przejdź do **Dashboards** → **Import** w menu bocznym
2. Wprowadź ID dashboard: `10991` (oficjalny dashboard RabbitMQ)
3. Kliknij **Load**
4. W polu **Select a Prometheus data source**, wybierz wcześniej skonfigurowane źródło danych
5. Kliknij **Import**

### Importowanie dashboardu dla monitorowania kolejek

1. W Grafanie, przejdź do **Dashboards** → **Import** w menu bocznym
2. Wprowadź ID dashboard: `12683` (dashboard dla RabbitMQ-Queue)
3. Kliknij **Load**
4. W polu **Select a Prometheus data source**, wybierz wcześniej skonfigurowane źródło danych
5. Kliknij **Import**

### Alternatywne metody importowania dashboardów

Możesz również pobrać dashboard JSON z repozytorium GitHub:

1. Pobierz plik JSON dashboardu z [oficjalnego repozytorium RabbitMQ](https://github.com/rabbitmq/rabbitmq-server/tree/main/deps/rabbitmq_prometheus/docker/grafana/dashboards)
2. W Grafanie, przejdź do **Dashboards** → **Import**
3. Kliknij **Upload JSON file** i wybierz pobrany plik
4. Wybierz źródło danych Prometheus
5. Kliknij **Import**

## Tworzenie własnego dashboardu RabbitMQ

Jeśli chcesz stworzyć własny dashboard dostosowany do monitorowania konkretnych kolejek, wykonaj następujące kroki:

1. W Grafanie, przejdź do **Dashboards** → **New dashboard**
2. Kliknij **Add new panel**

### Panel do monitorowania liczby wiadomości w kolejce

1. W górnej części edytora panelu, ustaw tytuł: "Messages in Queue"
2. W polu zapytania metryki (Query), wprowadź:

   ```
   rabbitmq_queue_messages{queue="task_queue", vhost="my_app_vhost"}
   ```

   > Uwaga: Zmień `queue="task_queue"` i `vhost="my_app_vhost"` na nazwy swojej kolejki i hosta wirtualnego.

3. W sekcji **Panel options**, rozwiń **Display name** i wprowadź: `{{queue}} - Messages`
4. W opcjach legendy wybierz, aby pokazywała etykiety i wartości
5. Kliknij **Apply** w prawym górnym rogu

### Panel do monitorowania szybkości publikowania/pobierania wiadomości

1. Dodaj nowy panel
2. Ustaw tytuł: "Message Rate"
3. W polu zapytania metryki, wprowadź dla publikowanych wiadomości:

   ```
   rate(rabbitmq_queue_messages_published_total{queue="task_queue", vhost="my_app_vhost"}[1m])
   ```

4. Dodaj kolejne zapytanie (przycisk "Add query") dla pobieranych wiadomości:

   ```
   rate(rabbitmq_queue_messages_delivered_total{queue="task_queue", vhost="my_app_vhost"}[1m])
   ```

5. W sekcji **Legend**, ustaw format: `{{queue}} - {{type}}`
6. Kliknij **Apply**

### Panel do monitorowania opóźnień w kolejce

1. Dodaj nowy panel
2. Ustaw tytuł: "Queue Latency (ms)"
3. W polu zapytania metryki, wprowadź:

   ```
   rabbitmq_queue_process_messages_latency_seconds{queue="task_queue", vhost="my_app_vhost"} * 1000
   ```

4. Zmień typ wykresu na "Gauge" lub "Stat", aby lepiej wizualizować opóźnienia
5. Kliknij **Apply**

### Tworzenie widoku dla wielu kolejek

Aby monitorować wiele kolejek na jednym panelu:

1. Dodaj nowy panel
2. Ustaw tytuł: "All Queues - Messages"
3. W polu zapytania metryki, wprowadź:

   ```
   rabbitmq_queue_messages{vhost="my_app_vhost"}
   ```

4. W sekcji **Legend**, ustaw format: `{{queue}}`
5. W ustawieniach panelu, włącz sortowanie według wartości (najwyższe na górze)
6. Kliknij **Apply**

### Zapisanie i organizacja dashboardu

1. W prawym górnym rogu kliknij ikonę dyskietki, aby zapisać dashboard
2. Nadaj dashboardowi nazwę, np. "RabbitMQ Queue Monitoring"
3. Opcjonalnie, dodaj opis i tagi
4. Możesz zorganizować panele poprzez ich przeciąganie i zmianę rozmiaru
5. Aby dodać sekcję, kliknij przycisk "Add panel" i wybierz "Add row"

## Przydatne metryki do monitorowania kolejek

Oto najważniejsze metryki Prometheus do monitorowania kolejek RabbitMQ:

### Metryki podstawowe

- `rabbitmq_queue_messages` - aktualna liczba wiadomości w kolejce
- `rabbitmq_queue_messages_ready` - liczba wiadomości gotowych do dostarczenia
- `rabbitmq_queue_messages_unacknowledged` - liczba niedostarczonych wiadomości

### Metryki tempa przetwarzania

- `rabbitmq_queue_messages_published_total` - całkowita liczba opublikowanych wiadomości
- `rabbitmq_queue_messages_delivered_total` - całkowita liczba dostarczonych wiadomości
- `rabbitmq_queue_messages_redelivered_total` - całkowita liczba ponownie dostarczonych wiadomości

### Metryki wydajności

- `rabbitmq_queue_process_memory_bytes` - pamięć używana przez proces kolejki
- `rabbitmq_queue_process_messages_latency_seconds` - opóźnienie w przetwarzaniu wiadomości

### Filtrowanie i agregacja

Powyższe metryki można filtrować według różnych etykiet:
- `queue` - nazwa kolejki
- `vhost` - host wirtualny
- `durable` - czy kolejka jest trwała
- `node` - węzeł RabbitMQ (w przypadku klastra)

Przykład agregacji dla wszystkich kolejek:
```
sum by (vhost) (rabbitmq_queue_messages)
```

## Konfiguracja alertów

Aby otrzymywać powiadomienia o problemach z kolejkami:

1. W panelu edycji, przejdź do zakładki **Alert**
2. Kliknij **Create Alert**
3. Ustaw warunek alertu, na przykład:
   - Nazwa: "Queue Overload Alert"
   - Warunek: "WHEN last() OF query(A, 1m, now) IS ABOVE 1000"
   - To wygeneruje alert, gdy liczba wiadomości w kolejce przekroczy 1000
4. Zdefiniuj czas ewaluacji i częstotliwość powiadomień
5. W sekcji **Notifications**, możesz skonfigurować kanał powiadomień (email, Slack, itp.)
6. Kliknij **Save** aby zapisać alert

### Przykłady użytecznych alertów

1. **Alert przy zbyt wielu wiadomościach w kolejce**:
   ```
   rabbitmq_queue_messages{queue="task_queue"} > 5000
   ```

2. **Alert przy braku konsumpcji**:
   ```
   rate(rabbitmq_queue_messages_delivered_total{queue="task_queue"}[5m]) == 0
   ```

3. **Alert przy wysokim tempie odrzucania wiadomości**:
   ```
   rate(rabbitmq_queue_messages_rejected_total{queue="task_queue"}[5m]) > 10
   ```

## Rozwiązywanie problemów z dashboardami

### Problemy z połączeniem Prometheus-Grafana

Jeśli podczas próby zapisania lub testowania źródła danych widzisz błąd podobny do:

```
Post "http://localhost:9090/api/v1/query": dial tcp 127.0.0.1:9090: connect: connection refused - There was an error returned querying the Prometheus API.
```

Typowe rozwiązania:

1. **Nieprawidłowy adres URL**:
   - W środowisku Docker, zmień `http://localhost:9090` na `http://prometheus:9090` 
   - Używaj nazwy serwisu z pliku docker-compose.yml, a nie localhost

2. **Problemy z siecią Docker**:
   - Upewnij się, że oba kontenery (Grafana i Prometheus) są w tej samej sieci Docker:
     ```bash
     docker-compose ps
     docker network inspect rabbitmq-network
     ```
   - Sprawdź, czy Prometheus nasłuchuje na porcie 9090 wewnątrz kontenera:
     ```bash
     docker-compose exec prometheus netstat -tlnp
     ```

3. **Sprawdź, czy Prometheus działa**:
   ```bash
   docker-compose ps prometheus
   docker-compose logs prometheus
   ```

4. **Dostęp do kontenerów**:
   - Spróbuj wykonać ping z kontenera Grafana do Prometheusa:
     ```bash
     docker-compose exec grafana ping prometheus
     ```
   - Sprawdź połączenie HTTP:
     ```bash
     docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/status/config
     ```

### Brak danych

Jeśli dashboard nie pokazuje danych:

1. Sprawdź, czy Prometheus ma dostęp do endpointu metryk RabbitMQ:
   - Przejdź do interfejsu Prometheusa (http://localhost:9090)
   - W zakładce **Status** → **Targets**, sprawdź czy cel RabbitMQ ma status UP
   
2. Sprawdź, czy wtyczka `rabbitmq_prometheus` jest włączona:
   - W interfejsie zarządzania RabbitMQ (http://localhost:15672)
   - Przejdź do zakładki **Admin** → **Plugins**, i upewnij się, że wtyczka jest włączona

3. Zweryfikuj poprawność zapytań metryki:
   - W Prometheusie, w zakładce **Graph**, przetestuj zapytanie
   - Sprawdź, czy nazwy kolejek i hostów wirtualnych są poprawne

### Nieprawidłowe wyświetlanie metryk

Jeśli metryki są wyświetlane niepoprawnie:

1. Sprawdź format jednostek w panelu
2. Upewnij się, że używasz odpowiednich funkcji (rate, increase) dla liczników
3. Dostosuj zakres czasowy dashboard lub poszczególnych paneli

### Problemy z wydajnością dashboardu

Jeśli dashboard działa wolno:

1. Zmniejsz zakres czasowy do krótszych okresów
2. Zmniejsz częstotliwość odświeżania
3. Ogranicz liczbę paneli pokazywanych jednocześnie
4. Dodaj filtrowanie, aby pokazywać tylko najważniejsze metryki

## Przykładowe zapytania dla typowych scenariuszy

### 1. Monitorowanie obciążenia poszczególnych kolejek

```
# Liczba wiadomości w kolejce
rabbitmq_queue_messages{vhost="my_app_vhost"}

# Tempo publikowania (wiadomości/s)
rate(rabbitmq_queue_messages_published_total{vhost="my_app_vhost"}[1m])

# Tempo dostarczania (wiadomości/s)
rate(rabbitmq_queue_messages_delivered_total{vhost="my_app_vhost"}[1m])
```

### 2. Wykrywanie nieaktywnych konsumentów

```
# Kolejki bez konsumentów
rabbitmq_queue_consumers == 0

# Kolejki z wiadomościami bez konsumentów
rabbitmq_queue_consumers == 0 and rabbitmq_queue_messages > 0
```

### 3. Identyfikacja zatorów w przetwarzaniu

```
# Różnica między publikowaniem a dostarczaniem
rate(rabbitmq_queue_messages_published_total{queue="task_queue"}[5m]) 
- 
rate(rabbitmq_queue_messages_delivered_total{queue="task_queue"}[5m])
```

### 4. Monitorowanie wykorzystania zasobów

```
# Pamięć używana przez procesy kolejek
rabbitmq_queue_process_memory_bytes{vhost="my_app_vhost"}

# Całkowite użycie pamięci przez RabbitMQ
rabbitmq_process_resident_memory_bytes{type="rabbitmq"}
```

---

Ten przewodnik powinien pomóc Ci skonfigurować efektywne dashboardy Grafana do monitorowania kolejek RabbitMQ. W miarę zdobywania doświadczenia możesz dostosowywać i rozbudowywać dashboardy, aby lepiej odpowiadały specyficznym potrzebom Twojego systemu.