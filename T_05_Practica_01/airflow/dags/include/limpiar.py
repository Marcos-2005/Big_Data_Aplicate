from pathlib import Path
import pandas as pd

from include.logging_utils import log_event


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Falta el fichero: {path}")
    return pd.read_csv(path, dtype=str).fillna("")


def _strip_df(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    return df


def _norm_eval(x: str) -> str:
    """
    Normaliza códigos de evaluación de ITACA a:
      - "1"  (1ª evaluación)
      - "2"  (2ª evaluación)
      - "FI" (final)
      - ""   (descartar: extraordinarias u otros)
    """
    s = (x or "").strip().upper()
    if not s:
        return ""

    # Extraordinaria / cosas que NO contamos
    if s == "EX":
        return ""  # fuera

    # Variantes de 1ª
    if s in ("1", "01", "P1"):
        return "1"

    # Variantes de 2ª
    if s in ("2", "02"):
        return "2"

    # Cualquier "F*" o finales -> FI
    if s == "FI" or s in ("FINAL", "FIN", "F", "FE", "FO", "FC", "FJ"):
        return "FI"
    if s.startswith("F"):  # F1,F2,F3,F4,F5...
        return "FI"

    # Otros códigos (PO, PE, P3, etc.) -> descartar
    return ""


def bronze_to_silver(year_label: str, bronze_dir: str, silver_dir: str, **context):
    bronze = Path(bronze_dir)
    silver = Path(silver_dir)
    silver.mkdir(parents=True, exist_ok=True)

    alumnos = _read_csv(bronze / f"alumnos_bronze_{year_label}.csv")
    modulos = _read_csv(bronze / f"modulos_bronze_{year_label}.csv")
    cursos = _read_csv(bronze / f"cursos_bronze_{year_label}.csv")
    califs = _read_csv(bronze / f"calificaciones_bronze_{year_label}.csv")

    # normalización suave (strip)
    alumnos = _strip_df(alumnos).drop_duplicates()
    modulos = _strip_df(modulos).drop_duplicates()
    cursos = _strip_df(cursos).drop_duplicates()
    califs = _strip_df(califs).drop_duplicates()

    # ✅ Filtro seguro: solo filtra calificaciones si id_alumno tiene valores reales
    if "id_alumno" in alumnos.columns and "alumno" in califs.columns:
        valid_ids = {x for x in alumnos["id_alumno"].astype(str).tolist() if x and x.strip()}
        if valid_ids:
            califs = califs[califs["alumno"].astype(str).isin(valid_ids)].copy()
        else:
            print(
                f"[SILVER] Aviso: id_alumno vacío en {year_label} -> NO se filtran calificaciones para no perder datos."
            )

    # ✅ Evaluaciones: normalizar + quitar extraordinarias (blancos)
    # OJO: no aplicamos regla 1º/2º/CE aquí porque en tu caso estaba eliminando 1 y 2.
    if "evaluacion" in califs.columns:
        califs["evaluacion"] = califs["evaluacion"].apply(_norm_eval)
        califs = califs[califs["evaluacion"] != ""].copy()

    # guardar silver
    alumnos.to_csv(silver / f"alumnos_silver_{year_label}.csv", index=False)
    modulos.to_csv(silver / f"modulos_silver_{year_label}.csv", index=False)
    cursos.to_csv(silver / f"cursos_silver_{year_label}.csv", index=False)
    califs.to_csv(silver / f"calificaciones_silver_{year_label}.csv", index=False)

    log_event(
        dag_id=context["dag"].dag_id,
        task_id=context["task"].task_id,
        stage="SILVER",
        status="SUCCESS",
        anyo=year_label,
        run_id=context.get("run_id"),
        logical_date=str(context.get("logical_date")),
        rows_alumnos=len(alumnos),
        rows_modulos=len(modulos),
        rows_cursos=len(cursos),
        rows_calificaciones=len(califs),
        message="SILVER generado desde BRONZE (strip + dedupe + filtro seguro + eval normalizada sin extraordinarias)",
    )