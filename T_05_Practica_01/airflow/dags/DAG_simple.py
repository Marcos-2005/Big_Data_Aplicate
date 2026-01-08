from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Define los argumentos por defecto para el DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define el DAG
with DAG(
    'flujo_descarga_procesamiento_simple',
    default_args=default_args,
    description='Un DAG simple para descargar y procesar un archivo',
    schedule=timedelta(days=1),
) as dag:

    # Tarea 1: Descargar un archivo (usando un operador de bash para simular)
    descargar_archivo = BashOperator(
        task_id='descargar_archivo',
        bash_command='echo "Simulando la descarga de un archivo..."'
    )

    # Tarea 2: Procesar el archivo descargado
    procesar_archivo = BashOperator(
        task_id='procesar_archivo',
        bash_command='echo "Procesando el archivo descargado..."'
    )

    # Establecer la dependencia entre las tareas
    descargar_archivo >> procesar_archivo
