import os
import sys
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

DAGS_PATH = os.path.dirname(os.path.abspath(__file__))
if DAGS_PATH not in sys.path:
    sys.path.insert(0, DAGS_PATH)

from include.bd import pipeline_gold_and_load

with DAG(
    dag_id="dag_db",
    schedule=None, 
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
    tags=["itaca", "gold", "mysql"],
) as dag:

    cargar = PythonOperator(
        task_id="gold_join_y_carga_mysql",
        python_callable=pipeline_gold_and_load,
        op_kwargs={
            "silver_dir": "/opt/airflow/dags/output/silver",
            "gold_dir": "/opt/airflow/dags/output/gold",
        },
    )
