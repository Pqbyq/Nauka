#!/bin/bash
# stop.sh - Skrypt do zatrzymywania środowiska Airflow

echo "====================================="
echo "  Zatrzymywanie Apache Airflow"
echo "====================================="

# Zatrzymanie kontenerów
echo "Zatrzymywanie kontenerów Docker..."
docker-compose down

echo "====================================="
echo "Apache Airflow został zatrzymany!"
echo "====================================="

# Wyświetlenie informacji o czyszczeniu (opcjonalnie)
echo "Jeśli chcesz całkowicie wyczyścić środowisko, użyj:"
echo "docker-compose down -v --rmi all --remove-orphans"
echo "UWAGA: Powyższe polecenie usunie wszystkie dane, w tym bazę danych!"