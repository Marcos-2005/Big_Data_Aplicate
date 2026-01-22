import os
import sys
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

DAGS_PATH = os.path.dirname(os.path.abspath(__file__))
if DAGS_PATH not in sys.path:
    sys.path.insert(0, DAGS_PATH)

from include.limpiar import limpiar_datos_por_anyo

with DAG(
    dag_id="dag_limpiar",
    schedule=None,  # lo dispara dag_datos
    start_date=pendulum.datetime(2025, 1, 1, tz="Europe/Madrid"),
    catchup=False,
) as dag:

    limpiar = PythonOperator(
        task_id="limpieza_silver",
        python_callable=limpiar_datos_por_anyo,
        op_args=[
            "/opt/airflow/dags/output/bronze",
            "/opt/airflow/dags/output/silver",
        ],
    )

    trigger_db = TriggerDagRunOperator(
        task_id="trigger_dag_db",
        trigger_dag_id="dag_db",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    limpiar >> trigger_db
