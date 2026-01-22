import os
import sys
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

DAGS_PATH = os.path.dirname(os.path.abspath(__file__))
if DAGS_PATH not in sys.path:
    sys.path.insert(0, DAGS_PATH)

from include.datos import xmls_to_bronze

with DAG(
    dag_id="dag_datos",
    schedule="0 2 * * *",  # diario 02:00 hora Madrid
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id="xmls_to_bronze",
        python_callable=xmls_to_bronze,
        op_args=[
            "/opt/airflow/dags/data/ITACA",      # 👈 carpeta, no lista
            "/opt/airflow/dags/output/bronze"
        ],
    )

    trigger_limpiar = TriggerDagRunOperator(
        task_id="trigger_dag_limpiar",
        trigger_dag_id="dag_limpiar",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    t1 >> trigger_limpiar
