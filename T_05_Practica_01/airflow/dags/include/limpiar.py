from pathlib import Path
import pandas as pd
from include.logging_utils import log_event


def _is_baja(estado: str) -> bool:
    """
    Decide si un alumno está de baja.
    Ajusta aquí si en tu dataset usas otro código.
    """
    if estado is None:
        return False
    s = str(estado).strip().upper()
    if s == "":
        return False
    # Casos típicos
    if s == "B":
        return True
    if "BAJA" in s:
        return True
    if "ANUL" in s:  # anulada/anulado
        return True
    return False


def limpiar_datos_por_anyo(bronze_dir: str, silver_dir: str, **context):
    bronze = Path(bronze_dir)
    silver = Path(silver_dir)
    silver.mkdir(parents=True, exist_ok=True)

    dag_id = context.get("dag").dag_id if context.get("dag") else "dag_limpiar"
    task_id = context.get("task").task_id if context.get("task") else "limpieza_silver"
    run_id = context.get("run_id")
    logical_date = str(context.get("logical_date")) if context.get("logical_date") else None

    # Detectamos años disponibles por alumnos_bronze_YYYY.csv
    years = []
    for p in bronze.glob("alumnos_bronze_*.csv"):
        try:
            year = int(p.stem.split("_")[-1])
            years.append(year)
        except Exception:
            pass
    years = sorted(set(years))

    if not years:
        raise FileNotFoundError(f"No encuentro alumnos_bronze_YYYY.csv en {bronze}")

    for anyo in years:
        alumnos_in = bronze / f"alumnos_bronze_{anyo}.csv"
        modulos_in = bronze / f"modulos_bronze_{anyo}.csv"
        cursos_in = bronze / f"cursos_bronze_{anyo}.csv"
        califs_in = bronze / f"calificaciones_bronze_{anyo}.csv"

        for f in [alumnos_in, modulos_in, cursos_in, califs_in]:
            if not f.exists():
                raise FileNotFoundError(f"No existe {f}")

        alumnos = pd.read_csv(alumnos_in, dtype=str).fillna("").drop_duplicates()
        modulos = pd.read_csv(modulos_in, dtype=str).fillna("").drop_duplicates()
        cursos = pd.read_csv(cursos_in, dtype=str).fillna("").drop_duplicates()
        califs = pd.read_csv(califs_in, dtype=str).fillna("").drop_duplicates()

        # =====================================================
        # REGLA: ELIMINAR SOLO LAS CALIFICACIONES DE ALUMNOS DE BAJA
        # (el alumno se mantiene en alumnos_silver)
        # =====================================================

        # Si no hay columna estado_matricula, no podemos identificar bajas
        if "estado_matricula" in alumnos.columns and "id_alumno" in alumnos.columns:
            alumnos["__baja__"] = alumnos["estado_matricula"].apply(_is_baja)
            ids_baja = set(alumnos.loc[alumnos["__baja__"] == True, "id_alumno"].astype(str))
        else:
            ids_baja = set()

        # Filtramos calificaciones: quitamos las de alumnos de baja
        if "alumno" not in califs.columns:
            raise ValueError(f"Falta columna alumno en {califs_in}")

        califs_ok = califs[~califs["alumno"].astype(str).isin(ids_baja)].copy()

        # Guardamos SILVER (alumnos NO se filtra)
        alumnos.drop(columns=["__baja__"], errors="ignore").to_csv(
            silver / f"alumnos_silver_{anyo}.csv", index=False
        )
        modulos.to_csv(silver / f"modulos_silver_{anyo}.csv", index=False)
        cursos.to_csv(silver / f"cursos_silver_{anyo}.csv", index=False)
        califs_ok.to_csv(silver / f"calificaciones_silver_{anyo}.csv", index=False)

        # LOG
        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="SILVER",
            status="SUCCESS",
            anyo=anyo,
            run_id=run_id,
            logical_date=logical_date,
            rows_alumnos=len(alumnos),
            rows_modulos=len(modulos),
            rows_cursos=len(cursos),
            rows_calificaciones=len(califs_ok),
            message=f"Calificaciones eliminadas para {len(ids_baja)} alumnos de baja",
        )

    print("✅ SILVER generado por año (calificaciones de bajas eliminadas)")
