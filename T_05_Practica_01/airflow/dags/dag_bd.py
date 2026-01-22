import os
import sys
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

DAGS_PATH = os.path.dirname(os.path.abspath(__file__))
if DAGS_PATH not in sys.path:
    sys.path.insert(0, DAGS_PATH)

from include.bd import pipeline_db

with DAG(
    dag_id="dag_db",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
) as dag:

    cargar = PythonOperator(
        task_id="cargar_mysql",
        python_callable=pipeline_db,
        op_args=[
            "/opt/airflow/dags/output/silver",
            "/opt/airflow/dags/output/gold",
        ],
    )
