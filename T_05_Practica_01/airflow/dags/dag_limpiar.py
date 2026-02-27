import os
import sys
import pendulum
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

DAGS_PATH = os.path.dirname(os.path.abspath(__file__))
if DAGS_PATH not in sys.path:
    sys.path.insert(0, DAGS_PATH)

from include.limpiar import bronze_to_silver

BRONZE_DIR = Path("/opt/airflow/dags/output/bronze")
SILVER_DIR = Path("/opt/airflow/dags/output/silver")

YEARS = ["2025_26", "2024_25", "2023_24"]

with DAG(
    dag_id="dag_limpiar",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
    max_active_runs=1,
    tags=["itaca", "silver"],
) as dag:

    silver_tasks = [
        PythonOperator(
            task_id=f"silver_{year}",
            python_callable=bronze_to_silver,
            op_kwargs={
                "year_label": year,
                "bronze_dir": str(BRONZE_DIR),
                "silver_dir": str(SILVER_DIR),
            },
        )
        for year in YEARS
    ]

    trigger_db = TriggerDagRunOperator(
        task_id="trigger_dag_db",
        trigger_dag_id="dag_db",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    for t in silver_tasks:
        t >> trigger_db