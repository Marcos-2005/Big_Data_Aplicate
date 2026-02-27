import os
from pathlib import Path
from typing import Dict, Iterable, Tuple
import pandas as pd
import mysql.connector

from include.logging_utils import log_event, get_mysql_config

YEARS = ["2025_26", "2024_25", "2023_24"]
T_CURSOS_MODULOS = os.getenv("T_CURSOS_MODULOS", "cursos_modulos")


# -------------------------
# IO
# -------------------------
def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Falta el fichero: {path}")
    return pd.read_csv(path, dtype=str).fillna("")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


# -------------------------
# Helpers
# -------------------------
def to_int_or_empty(x) -> str:
    s = str(x).strip() if x is not None else ""
    if s == "" or s.lower() == "nan":
        return ""
    try:
        return str(int(float(s)))
    except Exception:
        return s


def normalize_date(s: str) -> str:
    """Devuelve 'YYYY-MM-DD' o '' si no parsea."""
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return pd.to_datetime(s, format=fmt).date().isoformat()
        except Exception:
            pass
    return ""

def obtener_ancestro_por_nivel(codigo_inicial: str, saltos: int, mapa_padres: dict, mapa_nombres: dict) -> str:
    """Sube 'saltos' niveles en la jerarquía. Devuelve el nombre del ancestro o 'No definido'."""
    curr = codigo_inicial
    for _ in range(saltos):
        curr = mapa_padres.get(curr)
        if not curr or pd.isna(curr) or str(curr).strip().lower() == "nan":
            return "No definido"
    return mapa_nombres.get(curr, "No definido")

def dedupe_calificaciones(califs_gold: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Elimina duplicados reales asegurando 1 fila por (anyo, alumno, curso, contenido, evaluacion).
    Regla de resolución:
      - si hay varias filas para la misma clave: se queda con la nota máxima (MAX).
      - si no hay evaluacion: clave sin evaluacion.
    Devuelve (df_dedup, stats).
    """
    stats = {"before": len(califs_gold), "after": len(califs_gold), "dups_removed": 0}

    # Normaliza espacios por si acaso (reduce falsos duplicados)
    for c in ["anyo", "alumno", "curso", "contenido"]:
        if c in califs_gold.columns:
            califs_gold[c] = califs_gold[c].astype(str).str.strip()

    if "evaluacion" in califs_gold.columns:
        califs_gold["evaluacion"] = califs_gold["evaluacion"].astype(str).str.strip().str.upper()

        key = ["anyo", "alumno", "curso", "contenido", "evaluacion"]
        # Convierte nota a numérica para poder hacer MAX
        califs_gold["nota_numerica"] = pd.to_numeric(califs_gold["nota_numerica"], errors="coerce")

        df = (
            califs_gold
            .groupby(key, as_index=False, dropna=False)
            .agg({"nota_numerica": "max"})
        )

        # Vuelve a string (tu pipeline usa strings)
        df["nota_numerica"] = df["nota_numerica"].fillna("").apply(lambda x: "" if x == "" else str(int(x)) if pd.notna(x) else "")

    else:
        key = ["anyo", "alumno", "curso", "contenido"]
        califs_gold["nota_numerica"] = pd.to_numeric(califs_gold["nota_numerica"], errors="coerce")

        df = (
            califs_gold
            .groupby(key, as_index=False, dropna=False)
            .agg({"nota_numerica": "max"})
        )
        df["nota_numerica"] = df["nota_numerica"].fillna("").apply(lambda x: "" if x == "" else str(int(x)) if pd.notna(x) else "")

    stats["after"] = len(df)
    stats["dups_removed"] = stats["before"] - stats["after"]
    return df, stats

def executemany(cur, sql: str, rows: Iterable[Tuple]) -> None:
    rows = list(rows)
    if rows:
        cur.executemany(sql, rows)

def get_table_columns(cur, table: str) -> set:
    cur.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        """,
        (table,),
    )
    return {row[0] for row in cur.fetchall()}


# -------------------------
# DB
# -------------------------
def connect_mysql():
    cfg = get_mysql_config()
    return mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )


def delete_year(cur, table: str, year: str) -> None:
    cur.execute(f"DELETE FROM {table} WHERE anyo = %s", (year,))


# -------------------------
# GOLD builder (desde SILVER)
# -------------------------
def build_gold_from_silver(year: str, silver_dir: Path) -> Dict[str, pd.DataFrame]:
    alumnos = read_csv(silver_dir / f"alumnos_silver_{year}.csv")
    modulos = read_csv(silver_dir / f"modulos_silver_{year}.csv")
    cursos = read_csv(silver_dir / f"cursos_silver_{year}.csv")
    califs = read_csv(silver_dir / f"calificaciones_silver_{year}.csv")

    # Asegura columna anyo (tu silver puede no traerla)
    for df in (alumnos, modulos, cursos, califs):
        if "anyo" not in df.columns:
            df.insert(0, "anyo", year)

    # GOLD (selección final)
    alumnos_gold = alumnos[["anyo", "id_alumno", "fecha_nac", "sexo", "estado_matricula", "curso", "grupo", "turno"]].copy()

    modulos_gold = modulos[["anyo", "nombre_cas", "codigo", "curso"]].copy()

    cursos_gold = cursos[["anyo", "nombre_cas", "codigo", "padre"]].copy()

    calif_cols = ["anyo", "alumno", "curso", "contenido", "nota_numerica"]
    if "evaluacion" in califs.columns:
        calif_cols.append("evaluacion")

    califs_gold = califs[calif_cols].copy()

    califs_gold["nota_numerica"] = califs_gold["nota_numerica"].apply(to_int_or_empty)
    
    califs_gold, stats = dedupe_calificaciones(califs_gold)


    if "evaluacion" in califs_gold.columns:
        califs_gold["evaluacion"] = califs_gold["evaluacion"].astype(str).str.strip().str.upper()
        califs_gold["evaluacion"] = califs_gold["evaluacion"].replace(
            {"FINAL": "FI", "FIN": "FI", "F": "FI"}
        )
    
    # JOIN cursos + modulos -> cursos_modulos
    cursos_join = cursos_gold.rename(columns={"codigo": "codigo_curso", "nombre_cas": "nombre_curso"})
    modulos_join = modulos_gold.rename(columns={"curso": "codigo_curso", "codigo": "codigo_modulo", "nombre_cas": "nombre_modulo"})

    cursos_modulos = modulos_join.merge(
        cursos_join[["anyo", "codigo_curso", "nombre_curso"]],
        on=["anyo", "codigo_curso"],
        how="left",
    )
    
    mapa_padres = dict(zip(cursos_gold["codigo"], cursos_gold["padre"]))
    mapa_nombres = dict(zip(cursos_gold["codigo"], cursos_gold["nombre_cas"]))

    cursos_modulos["ciclo"] = cursos_modulos["codigo_curso"].apply(
        lambda x: obtener_ancestro_por_nivel(x, 1, mapa_padres, mapa_nombres)
    )
    cursos_modulos["grado"] = cursos_modulos["codigo_curso"].apply(
        lambda x: obtener_ancestro_por_nivel(x, 2, mapa_padres, mapa_nombres)
    )
    cursos_modulos["familia"] = cursos_modulos["codigo_curso"].apply(
        lambda x: obtener_ancestro_por_nivel(x, 3, mapa_padres, mapa_nombres)
    )

    return {
        "Alumnos": alumnos_gold,
        "Modulos": modulos_gold,
        "Cursos": cursos_gold,
        "Calificaciones": califs_gold,
        T_CURSOS_MODULOS: cursos_modulos,
    }


def persist_gold_year(year: str, gold_dir: Path, tables: Dict[str, pd.DataFrame]) -> None:
    write_csv(tables["Alumnos"], gold_dir / f"alumnos_gold_{year}.csv")
    write_csv(tables["Modulos"], gold_dir / f"modulos_gold_{year}.csv")
    write_csv(tables["Cursos"], gold_dir / f"cursos_gold_{year}.csv")
    write_csv(tables["Calificaciones"], gold_dir / f"calificaciones_gold_{year}.csv")
    write_csv(tables[T_CURSOS_MODULOS], gold_dir / f"cursos_modulos_gold_{year}.csv")


# -------------------------
# LOAD
# -------------------------

def load_year(cur, year: str, tables: Dict[str, pd.DataFrame]) -> None:
    alumnos = tables["Alumnos"]
    modulos = tables["Modulos"]
    cursos = tables["Cursos"]
    califs = tables["Calificaciones"]
    cursos_modulos = tables[T_CURSOS_MODULOS]

    # Idempotencia
    for t in ["Alumnos", "Modulos", "Cursos", "Calificaciones", T_CURSOS_MODULOS]:
        delete_year(cur, t, year)

    # Inserts
    executemany(
        cur,
        """
        INSERT INTO Alumnos (anyo, id_alumno, fecha_nac, sexo, estado_matricula, curso, grupo, turno)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            (
                r.get("anyo", year),
                r.get("id_alumno", ""),
                normalize_date(r.get("fecha_nac", "")),
                r.get("sexo", ""),
                r.get("estado_matricula", ""),
                r.get("curso", ""),
                r.get("grupo", ""),
                r.get("turno", ""),
            )
            for _, r in alumnos.iterrows()
        ),
    )

    executemany(
        cur,
        "INSERT INTO Modulos (anyo, nombre_cas, codigo, curso) VALUES (%s, %s, %s, %s)",
        (
            (r.get("anyo", year), r.get("nombre_cas", ""), r.get("codigo", ""), r.get("curso", ""))
            for _, r in modulos.iterrows()
        ),
    )

    executemany(
        cur,
        "INSERT INTO Cursos (anyo, nombre_cas, codigo, padre) VALUES (%s, %s, %s, %s)",
        (
            (r.get("anyo", year), r.get("nombre_cas", ""), r.get("codigo", ""), r.get("padre", ""))
            for _, r in cursos.iterrows()
        ),
    )

    # ✅ Calificaciones con evaluacion (si existe en el DF y en la tabla)
    cols = get_table_columns(cur, "Calificaciones")  # necesitas tener esta función en tu bd.py

    if "evaluacion" in cols and "evaluacion" in califs.columns:
        executemany(
            cur,
            """
            INSERT INTO Calificaciones (anyo, alumno, curso, contenido, nota_numerica, evaluacion)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                (
                    r.get("anyo", year),
                    r.get("alumno", ""),
                    r.get("curso", ""),
                    r.get("contenido", ""),
                    None if r.get("nota_numerica", "") == "" else r.get("nota_numerica"),
                    r.get("evaluacion", ""),
                )
                for _, r in califs.iterrows()
            ),
        )
    else:
        executemany(
            cur,
            "INSERT INTO Calificaciones (anyo, alumno, curso, contenido, nota_numerica) VALUES (%s, %s, %s, %s, %s)",
            (
                (
                    r.get("anyo", year),
                    r.get("alumno", ""),
                    r.get("curso", ""),
                    r.get("contenido", ""),
                    None if r.get("nota_numerica", "") == "" else r.get("nota_numerica"),
                    r.get("evaluacion", ""),
                )
                for _, r in califs.iterrows()
            ),
        )

    cols_cm = get_table_columns(cur, T_CURSOS_MODULOS)

    tiene_ciclo = "ciclo" in cols_cm and "ciclo" in cursos_modulos.columns
    tiene_grado = "grado" in cols_cm and "grado" in cursos_modulos.columns
    tiene_familia = "familia" in cols_cm and "familia" in cursos_modulos.columns

    base_cols = ["anyo", "codigo_modulo", "nombre_modulo", "codigo_curso", "nombre_curso"]
    extra_cols = []
    if tiene_ciclo:
        extra_cols.append("ciclo")
    if tiene_grado:
        extra_cols.append("grado")
    if tiene_familia:
        extra_cols.append("familia")

    all_cols = base_cols + extra_cols
    placeholders = ", ".join(["%s"] * len(all_cols))
    cols_sql = ", ".join(all_cols)

    executemany(
        cur,
        f"INSERT INTO {T_CURSOS_MODULOS} ({cols_sql}) VALUES ({placeholders})",
        (
            tuple(r.get(c, year if c == "anyo" else "") for c in all_cols)
            for _, r in cursos_modulos.iterrows()
        ),
    )


# -------------------------
# Pipeline callable
# -------------------------
def pipeline_gold_and_load(silver_dir: str, gold_dir: str, **context) -> None:
    silver_dir = Path(silver_dir)
    gold_dir = Path(gold_dir)
    gold_dir.mkdir(parents=True, exist_ok=True)

    dag_id = context["dag"].dag_id
    task_id = context["task"].task_id
    run_id = context.get("run_id")
    logical_date = str(context.get("logical_date"))

    conn = connect_mysql()
    cur = conn.cursor()

    try:
        totals = {"al": 0, "mo": 0, "cu": 0, "ca": 0, "cm": 0}

        for year in YEARS:
            tables = build_gold_from_silver(year, silver_dir)
            persist_gold_year(year, gold_dir, tables)  # ✅ vuelve a generarte gold

            load_year(cur, year, tables)

            totals["al"] += len(tables["Alumnos"])
            totals["mo"] += len(tables["Modulos"])
            totals["cu"] += len(tables["Cursos"])
            totals["ca"] += len(tables["Calificaciones"])
            totals["cm"] += len(tables[T_CURSOS_MODULOS])

            log_event(
                dag_id=dag_id,
                task_id=task_id,
                stage="LOAD",
                status="SUCCESS",
                anyo=year,
                run_id=run_id,
                logical_date=logical_date,
                rows_alumnos=len(tables["Alumnos"]),
                rows_modulos=len(tables["Modulos"]),
                rows_cursos=len(tables["Cursos"]),
                rows_calificaciones=len(tables["Calificaciones"]),
                message=f"LOAD OK year={year} (join->{T_CURSOS_MODULOS}, filas_join={len(tables[T_CURSOS_MODULOS])})",
            )
            conn.commit()

        conn.commit()

        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="LOAD",
            status="SUCCESS",
            anyo=None,
            run_id=run_id,
            logical_date=logical_date,
            rows_alumnos=totals["al"],
            rows_modulos=totals["mo"],
            rows_cursos=totals["cu"],
            rows_calificaciones=totals["ca"],
            message=f"LOAD TOTAL OK (join->{T_CURSOS_MODULOS}, filas_join={totals['cm']})",
        )

    except Exception as e:
        conn.rollback()
        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="LOAD",
            status="FAIL",
            anyo=None,
            run_id=run_id,
            logical_date=logical_date,
            message=f"Error carga MySQL: {e}",
        )
        raise

    finally:
        cur.close()
        conn.close()
