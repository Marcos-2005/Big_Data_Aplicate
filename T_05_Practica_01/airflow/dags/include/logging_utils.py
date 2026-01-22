import os
import mysql.connector
from datetime import datetime

MYSQL_HOST = os.getenv("MYSQL_HOST", "nifi.cz2d9bplmbsl.us-east-1.rds.amazonaws.com")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Marcos2005")
MYSQL_DB = os.getenv("MYSQL_DB", "airflow")

def _connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
    )

def ensure_log_table():
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS etl_log (
              id BIGINT AUTO_INCREMENT PRIMARY KEY,
              ts DATETIME NOT NULL,
              dag_id VARCHAR(128) NOT NULL,
              task_id VARCHAR(128) NOT NULL,
              run_id VARCHAR(256) NULL,
              logical_date VARCHAR(64) NULL,
              stage VARCHAR(32) NOT NULL,
              anyo INT NULL,
              status VARCHAR(16) NOT NULL,
              rows_alumnos INT NULL,
              rows_modulos INT NULL,
              rows_cursos INT NULL,
              rows_calificaciones INT NULL,
              message VARCHAR(1024) NULL
            )
            """
        )
    finally:
        cur.close()
        conn.close()

def log_event(
    dag_id: str,
    task_id: str,
    stage: str,
    status: str,
    anyo: int | None = None,
    run_id: str | None = None,
    logical_date: str | None = None,
    rows_alumnos: int | None = None,
    rows_modulos: int | None = None,
    rows_cursos: int | None = None,
    rows_calificaciones: int | None = None,
    message: str | None = None,
):
    ensure_log_table()
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO etl_log
            (ts, dag_id, task_id, run_id, logical_date, stage, anyo, status,
             rows_alumnos, rows_modulos, rows_cursos, rows_calificaciones, message)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                datetime.now(),
                dag_id,
                task_id,
                run_id,
                logical_date,
                stage,
                anyo,
                status,
                rows_alumnos,
                rows_modulos,
                rows_cursos,
                rows_calificaciones,
                message,
            ),
        )
    finally:
        cur.close()
        conn.close()
