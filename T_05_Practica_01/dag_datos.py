from __future__ import annotations

from pathlib import Path
import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator

from include.alumnos_csv import crear_csv_ejemplo, transformar_csv, generar_resumen

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_CSV = DATA_DIR / "clases.xml"
INPUT_CSV = DATA_DIR / "clases.csv"
OUTPUT_CSV = OUTPUT_DIR / "alumnos_notas_transformado.csv"
SUMMARY_TXT = OUTPUT_DIR / "resumen.txt"


def _task_crear_csv(**context):
    return crear_csv_ejemplo(INPUT_CSV)


def _task_transformar(**context):
    return transformar_csv(INPUT_CSV, OUTPUT_CSV)


def _task_resumen(**context):
    return generar_resumen(OUTPUT_CSV, SUMMARY_TXT)


with DAG(
    dag_id="csv_alumnos_transform_dag",
    start_date=pendulum.datetime(2025, 12, 1, tz="Europe/Madrid"),
    schedule=None,
    catchup=False,
    tags=["ejemplo", "csv", "pythonoperator"],
) as dag:

    t1 = PythonOperator(
        task_id="crear_csv_ejemplo", 
        python_callable=_task_crear_csv
    )
    t2 = PythonOperator(
        task_id="transformar_csv", 
        python_callable=_task_transformar
    )
    t3 = PythonOperator(
        task_id="resumen", 
        python_callable=_task_resumen
    )

    t1 >> t2 >> t3