import os
from pathlib import Path
import pandas as pd
import mysql.connector

from include.logging_utils import log_event


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
        autocommit=False,
    )


def _to_int_or_empty(x) -> str:
    """Normaliza nota_numerica a entero string si puede, si no deja vacío o el valor."""
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return ""
    try:
        return str(int(float(s)))
    except Exception:
        return s


def _years_in_silver(silver: Path) -> list[int]:
    years = []
    for p in silver.glob("alumnos_silver_*.csv"):
        try:
            years.append(int(p.stem.split("_")[-1]))
        except Exception:
            pass
    return sorted(set(years))


def generar_gold_desde_silver(silver_dir: str, gold_dir: str, **context):
    """
    Genera CSV 'gold' desde los CSV 'silver' (por año), alineados con el DW/BD.
    """
    silver = Path(silver_dir)
    gold = Path(gold_dir)
    gold.mkdir(parents=True, exist_ok=True)

    dag_id = context.get("dag").dag_id if context.get("dag") else "dag_db"
    task_id = context.get("task").task_id if context.get("task") else "cargar_mysql"
    run_id = context.get("run_id")
    logical_date = str(context.get("logical_date")) if context.get("logical_date") else None

    years = _years_in_silver(silver)
    if not years:
        raise FileNotFoundError(f"No encuentro alumnos_silver_YYYY.csv en {silver}")

    for anyo in years:
        alumnos_path = silver / f"alumnos_silver_{anyo}.csv"
        modulos_path = silver / f"modulos_silver_{anyo}.csv"
        cursos_path = silver / f"cursos_silver_{anyo}.csv"
        califs_path = silver / f"calificaciones_silver_{anyo}.csv"

        for p in [alumnos_path, modulos_path, cursos_path, califs_path]:
            if not p.exists():
                raise FileNotFoundError(f"No existe el fichero requerido: {p}")

        alumnos = pd.read_csv(alumnos_path, dtype=str).fillna("")
        modulos = pd.read_csv(modulos_path, dtype=str).fillna("")
        cursos = pd.read_csv(cursos_path, dtype=str).fillna("")
        califs = pd.read_csv(califs_path, dtype=str).fillna("")

        # --- GOLD: Alumnos (exacto para tabla Alumnos)
        alumnos_gold = alumnos[[
            "id_alumno", "fecha_nac", "sexo", "estado_matricula", "curso", "grupo", "turno"
        ]].copy()
        alumnos_gold.insert(0, "anyo", str(anyo))
        alumnos_gold.to_csv(gold / f"alumnos_gold_{anyo}.csv", index=False)

        # --- GOLD: Modulos (tabla Modulos)
        modulos_gold = modulos[["nombre_cas", "codigo", "curso"]].copy()
        modulos_gold.insert(0, "anyo", str(anyo))
        modulos_gold.to_csv(gold / f"modulos_gold_{anyo}.csv", index=False)

        # --- GOLD: Cursos (tabla Cursos)
        cursos_gold = cursos[["nombre_cas", "codigo", "padre"]].copy()
        cursos_gold.insert(0, "anyo", str(anyo))
        cursos_gold.to_csv(gold / f"cursos_gold_{anyo}.csv", index=False)

        # --- GOLD: Calificaciones (tabla Calificaciones)
        califs_gold = califs[["alumno", "curso", "contenido", "nota_numerica"]].copy()
        califs_gold["nota_numerica"] = califs_gold["nota_numerica"].apply(_to_int_or_empty)
        califs_gold.insert(0, "anyo", str(anyo))
        califs_gold.to_csv(gold / f"calificaciones_gold_{anyo}.csv", index=False)

        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="GOLD",
            status="SUCCESS",
            anyo=anyo,
            run_id=run_id,
            logical_date=logical_date,
            rows_alumnos=len(alumnos_gold),
            rows_modulos=len(modulos_gold),
            rows_cursos=len(cursos_gold),
            rows_calificaciones=len(califs_gold),
            message=f"GOLD generado desde SILVER para año {anyo}",
        )

    print("✅ GOLD generado desde SILVER (por año)")


def cargar_mysql_desde_gold(gold_dir: str, **context):
    """
    Carga MySQL usando los CSV gold (por año).
    """
    gold = Path(gold_dir)

    dag_id = context.get("dag").dag_id if context.get("dag") else "dag_db"
    task_id = context.get("task").task_id if context.get("task") else "cargar_mysql"
    run_id = context.get("run_id")
    logical_date = str(context.get("logical_date")) if context.get("logical_date") else None

    # años por alumnos_gold_YYYY.csv
    years = []
    for p in gold.glob("alumnos_gold_*.csv"):
        try:
            years.append(int(p.stem.split("_")[-1]))
        except Exception:
            pass
    years = sorted(set(years))
    if not years:
        raise FileNotFoundError(f"No encuentro alumnos_gold_YYYY.csv en {gold}")

    conn = _connect()
    cur = conn.cursor()

    try:
        for anyo in years:
            alumnos_path = gold / f"alumnos_gold_{anyo}.csv"
            modulos_path = gold / f"modulos_gold_{anyo}.csv"
            cursos_path = gold / f"cursos_gold_{anyo}.csv"
            califs_path = gold / f"calificaciones_gold_{anyo}.csv"

            for p in [alumnos_path, modulos_path, cursos_path, califs_path]:
                if not p.exists():
                    raise FileNotFoundError(f"No existe el fichero requerido: {p}")

            alumnos = pd.read_csv(alumnos_path, dtype=str).fillna("")
            modulos = pd.read_csv(modulos_path, dtype=str).fillna("")
            cursos = pd.read_csv(cursos_path, dtype=str).fillna("")
            califs = pd.read_csv(califs_path, dtype=str).fillna("")

            # ALUMNOS
            cur.execute("DELETE FROM Alumnos WHERE anyo = %s", (anyo,))
            cur.executemany(
                """
                INSERT INTO Alumnos (anyo, id_alumno, fecha_nac, sexo, estado_matricula, curso, grupo, turno)
                VALUES (%s, %s, STR_TO_DATE(%s, '%%d/%%m/%%Y'), %s, %s, %s, %s, %s)
                """,
                [
                    (
                        row.get("anyo", anyo),
                        row.get("id_alumno", ""),
                        row.get("fecha_nac", ""),
                        row.get("sexo", ""),
                        row.get("estado_matricula", ""),
                        row.get("curso", ""),
                        row.get("grupo", ""),
                        row.get("turno", ""),
                    )
                    for _, row in alumnos.iterrows()
                ],
            )

            # MODULOS
            cur.execute("DELETE FROM Modulos WHERE anyo = %s", (anyo,))
            cur.executemany(
                """
                INSERT INTO Modulos (anyo, nombre_cas, codigo, curso)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (
                        row.get("anyo", anyo),
                        row.get("nombre_cas", ""),
                        row.get("codigo", ""),
                        row.get("curso", ""),
                    )
                    for _, row in modulos.iterrows()
                ],
            )

            # CURSOS
            cur.execute("DELETE FROM Cursos WHERE anyo = %s", (anyo,))
            cur.executemany(
                """
                INSERT INTO Cursos (anyo, nombre_cas, codigo, padre)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (
                        row.get("anyo", anyo),
                        row.get("nombre_cas", ""),
                        row.get("codigo", ""),
                        row.get("padre", ""),
                    )
                    for _, row in cursos.iterrows()
                ],
            )

            # CALIFICACIONES
            cur.execute("DELETE FROM Calificaciones WHERE anyo = %s", (anyo,))
            cur.executemany(
                """
                INSERT INTO Calificaciones (anyo, alumno, curso, contenido, nota_numerica)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (
                        row.get("anyo", anyo),
                        row.get("alumno", ""),
                        row.get("curso", ""),
                        row.get("contenido", ""),
                        row.get("nota_numerica", ""),
                    )
                    for _, row in califs.iterrows()
                ],
            )

            # cursos_modulos (derivada)
            cursos_map = {r.get("codigo", ""): r.get("nombre_cas", "") for _, r in cursos.iterrows()}

            cur.execute("DELETE FROM cursos_modulos WHERE anyo = %s", (anyo,))
            cur.executemany(
                """
                INSERT INTO cursos_modulos (anyo, codigo_modulo, nombre_modulo, codigo_curso, nombre_curso)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (
                        anyo,
                        row.get("codigo", ""),
                        row.get("nombre_cas", ""),
                        row.get("curso", ""),
                        cursos_map.get(row.get("curso", ""), ""),
                    )
                    for _, row in modulos.iterrows()
                ],
            )

            log_event(
                dag_id=dag_id,
                task_id=task_id,
                stage="DB",
                status="SUCCESS",
                anyo=anyo,
                run_id=run_id,
                logical_date=logical_date,
                rows_alumnos=len(alumnos),
                rows_modulos=len(modulos),
                rows_cursos=len(cursos),
                rows_calificaciones=len(califs),
                message=f"Carga MySQL desde GOLD completada para año {anyo}",
            )

        conn.commit()
        print("✅ Carga a MySQL desde GOLD completada")

    except Exception as e:
        conn.rollback()
        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="DB",
            status="FAIL",
            anyo=None,
            run_id=run_id,
            logical_date=logical_date,
            message=f"Error: {repr(e)}",
        )
        raise
    finally:
        cur.close()
        conn.close()


def pipeline_db(silver_dir: str, gold_dir: str, **context):
    """
    Pipeline completo de la capa DB:
    1) Genera GOLD desde SILVER
    2) Carga MySQL desde GOLD
    """
    generar_gold_desde_silver(silver_dir, gold_dir, **context)
    cargar_mysql_desde_gold(gold_dir, **context)
