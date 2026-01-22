import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
import hashlib
import os
import re

from include.logging_utils import log_event

SALT = os.getenv("ANON_SALT", "salt-secreta-cambia-esto")


def hash_id(value: str) -> str:
    if value is None:
        return ""
    v = value.strip().upper()
    if v == "":
        return ""
    return hashlib.sha256((SALT + v).encode("utf-8")).hexdigest()


def _anyo_from_filename(xml_path: str) -> int:
    """
    varios_25-26_... -> 2025
    varios_24-25_... -> 2024
    varios_23-24_... -> 2023
    """
    name = Path(xml_path).name
    m = re.search(r"varios_(\d{2})-\d{2}", name)
    if not m:
        raise ValueError(f"No puedo extraer año del archivo: {name}")
    yy = int(m.group(1))
    return 2000 + yy


def _extract_tables_from_xml(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    alumnos = []
    for a in root.findall(".//alumno"):
        alumnos.append({
            "id_alumno": a.get("NIA"),
            "documento_hash": hash_id(a.get("documento")),
            "fecha_nac": a.get("fecha_nac"),
            "sexo": a.get("sexo"),
            "estado_matricula": a.get("estado_matricula"),
            "curso": a.get("curso"),
            "grupo": a.get("grupo"),
            "turno": a.get("turno"),
        })

    modulos = []
    for m in root.findall(".//contenido"):
        modulos.append({
            "codigo": m.get("codigo"),
            "nombre_cas": m.get("nombre_cas"),
            "curso": m.get("curso"),
        })

    cursos = []
    for c in root.findall(".//curso"):
        cursos.append({
            "codigo": c.get("codigo"),
            "nombre_cas": c.get("nombre_cas"),
            "padre": c.get("padre"),
        })

    califs = []
    for c in root.findall(".//calificacion"):
        califs.append({
            "alumno": c.get("alumno"),
            "curso": c.get("curso"),
            "contenido": c.get("contenido"),
            "nota_numerica": c.get("nota_numerica"),
            "evaluacion": c.get("evaluacion"),
        })

    return alumnos, modulos, cursos, califs


def xmls_to_bronze(itaca_dir: str, out_dir: str, **context):
    itaca_dir = Path(itaca_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Coge TODOS los .xml que haya
    xml_paths = sorted([str(p) for p in itaca_dir.glob("*.xml")])

    if not xml_paths:
        raise FileNotFoundError(f"No hay XML en {itaca_dir}")

    dag_id = context.get("dag").dag_id if context.get("dag") else "dag_datos"
    task_id = context.get("task").task_id if context.get("task") else "xmls_to_bronze"
    run_id = context.get("run_id")
    logical_date = str(context.get("logical_date")) if context.get("logical_date") else None

    # Agrupar por año
    grouped: dict[int, list[str]] = {}
    for p in xml_paths:
        anyo = _anyo_from_filename(p)
        grouped.setdefault(anyo, []).append(p)

    for anyo, paths in grouped.items():
        all_alumnos, all_modulos, all_cursos, all_califs = [], [], [], []

        for p in paths:
            alumnos, modulos, cursos, califs = _extract_tables_from_xml(p)
            all_alumnos.extend(alumnos)
            all_modulos.extend(modulos)
            all_cursos.extend(cursos)
            all_califs.extend(califs)

        df_al = pd.DataFrame(all_alumnos).drop_duplicates()
        df_mo = pd.DataFrame(all_modulos).drop_duplicates()
        df_cu = pd.DataFrame(all_cursos).drop_duplicates()
        df_ca = pd.DataFrame(all_califs).drop_duplicates()

        df_al.to_csv(out_dir / f"alumnos_bronze_{anyo}.csv", index=False)
        df_mo.to_csv(out_dir / f"modulos_bronze_{anyo}.csv", index=False)
        df_cu.to_csv(out_dir / f"cursos_bronze_{anyo}.csv", index=False)
        df_ca.to_csv(out_dir / f"calificaciones_bronze_{anyo}.csv", index=False)

        log_event(
            dag_id=dag_id,
            task_id=task_id,
            stage="BRONZE",
            status="SUCCESS",
            anyo=anyo,
            run_id=run_id,
            logical_date=logical_date,
            rows_alumnos=len(df_al),
            rows_modulos=len(df_mo),
            rows_cursos=len(df_cu),
            rows_calificaciones=len(df_ca),
            message=f"BRONZE generado desde {len(paths)} XML(s) encontrados en {itaca_dir} para año {anyo}",
        )

    print("✅ BRONZE generado por año desde todos los XML detectados")
