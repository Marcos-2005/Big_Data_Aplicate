import os
import sys
import pendulum
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Asegura que /opt/airflow/dags está en el path para poder importar include.*
DAGS_ROOT = str(Path(__file__).resolve().parent)
if DAGS_ROOT not in sys.path:
    sys.path.insert(0, DAGS_ROOT)

from include.datos import xml_to_bronze

ITACA_DIR = Path("/opt/airflow/dags/data/ITACA")
BRONZE_DIR = Path("/opt/airflow/dags/output/bronze")

SOURCES = [
    ("2025_26", ITACA_DIR / "varios_25-26_anon_01.xml"),
    ("2024_25", ITACA_DIR / "varios_24-25_anon.xml"),
    ("2023_24", ITACA_DIR / "varios_23-24_anon.xml"),
]

with DAG(
    dag_id="dag_datos",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
    max_active_runs=1,
    tags=["itaca", "bronze"],
) as dag:

    bronze_tasks = [
        PythonOperator(
            task_id=f"bronze_{year}",
            python_callable=xml_to_bronze,
            op_kwargs={
                "xml_path": str(xml_path),
                "year_label": year,
                "out_dir": str(BRONZE_DIR),
            },
        )
        for year, xml_path in SOURCES
    ]

    trigger_limpiar = TriggerDagRunOperator(
        task_id="trigger_dag_limpiar",
        trigger_dag_id="dag_limpiar",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    for t in bronze_tasks:
        t >> trigger_limpiar