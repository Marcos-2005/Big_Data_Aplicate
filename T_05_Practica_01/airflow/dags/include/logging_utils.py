import os
import mysql.connector

# ✅ OPCIÓN 1: Airflow Connection "airflow"
def get_mysql_config():

    try:
        from airflow.hooks.base import BaseHook
        c = BaseHook.get_connection("airflow")
        return {
            "host": c.host,
            "port": c.port or 3306,
            "user": c.login,
            "password": c.password,
            "database": c.schema,
        }
    except Exception:
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DB", "airflow")

        if not password:
            raise RuntimeError(
                "Falta MYSQL_PASSWORD. No pongas contraseñas en el código: "
                "usa Airflow Connection 'airflow' o exporta MYSQL_PASSWORD."
            )

        return {"host": host, "port": port, "user": user, "password": password, "database": database}


def _connect():
    cfg = get_mysql_config()
    return mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=True,
    )


def log_event(
    dag_id: str,
    task_id: str,
    stage: str,
    status: str,
    anyo: str = None,
    run_id: str = None,
    logical_date: str = None,
    rows_alumnos: int = None,
    rows_modulos: int = None,
    rows_cursos: int = None,
    rows_calificaciones: int = None,
    message: str = None,
):
    """
    Inserta un registro en etl_log.
    Necesitas tener creada la tabla etl_log en tu MySQL.
    """
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO etl_log
            (dag_id, task_id, stage, status, anyo, run_id, logical_date,
             rows_alumnos, rows_modulos, rows_cursos, rows_calificaciones, message)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                dag_id, task_id, stage, status, anyo, run_id, logical_date,
                rows_alumnos, rows_modulos, rows_cursos, rows_calificaciones, message
            ),
        )
    finally:
        cur.close()
        conn.close()
