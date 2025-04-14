"""
Moduł do zapisywania danych do plików CSV
"""
import logging
import pandas as pd
import csv
import os
from datetime import datetime
import sys

# Dodanie ścieżki projektu do sys.path, aby można było importować z config
sys.path.append('/opt/airflow')
from modules.config.config import DATA_FOLDER

logger = logging.getLogger(__name__)

def save_to_csv(**kwargs):
    """
    Zapisuje przetworzone dane do pliku CSV
    
    Args:
        **kwargs: Argumenty przekazane przez Airflow, w tym ti (TaskInstance)
        
    Returns:
        str: Ścieżka do zapisanego pliku CSV lub None w przypadku błędu
    """
    ti = kwargs['ti']
    processed_data = ti.xcom_pull(task_ids='process_weather_data')
    
    if not processed_data:
        logger.warning("Brak danych do zapisania!")
        return None
    
    try:
        # Upewnij się, że folder istnieje
        os.makedirs(DATA_FOLDER, exist_ok=True)
        
        # Utwórz nazwę pliku na podstawie aktualnej daty
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f"{DATA_FOLDER}/weather_data_{timestamp}.csv"
        
        # Zapisz dane do pliku CSV
        df = pd.DataFrame(processed_data)
        df.to_csv(csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
        
        logger.info(f"Zapisano dane do pliku: {csv_file}")
        return csv_file
        
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania danych do CSV: {e}")
        return None