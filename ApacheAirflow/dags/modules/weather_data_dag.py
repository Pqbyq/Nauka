"""
Główny plik DAG integrujący wszystkie komponenty
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import modułów projektu
from modules.extractors.weather_api import fetch_weather_data
from modules.processors.weather_processor import process_weather_data
from modules.loaders.csv_loader import save_to_csv

# Import konfiguracji
import sys
sys.path.append('/opt/airflow')
from modules.config.config import DEFAULT_SCHEDULE_INTERVAL

# Domyślne argumenty dla DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definicja DAG
with DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='Pobiera, przetwarza i zapisuje dane pogodowe z API',
    schedule_interval=DEFAULT_SCHEDULE_INTERVAL,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['weather', 'api', 'data_processing'],
) as dag:

    # Definicja zadań
    t1 = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_weather_data,
        provide_context=True,
    )
    
    t2 = PythonOperator(
        task_id='process_weather_data',
        python_callable=process_weather_data,
        provide_context=True,
    )
    
    t3 = PythonOperator(
        task_id='save_to_csv',
        python_callable=save_to_csv,
        provide_context=True,
    )
    
    # Definicja zależności między zadaniami: t1 -> t2 -> t3
    t1 >> t2 >> t3