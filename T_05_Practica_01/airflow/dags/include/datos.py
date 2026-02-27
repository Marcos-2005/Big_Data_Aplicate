from pathlib import Path
import hashlib
import pandas as pd
import xml.etree.ElementTree as ET

from include.logging_utils import log_event


def sha256(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _pick(node: ET.Element, *keys: str) -> str:
    for k in keys:
        v = node.get(k)
        if v and str(v).strip():
            return str(v).strip()

    for k in keys:
        child = node.find(k)
        if child is not None and (child.text or "").strip():
            return child.text.strip()

    return ""


def _extract_tables_from_xml(xml_path: Path, year_label: str):
    root = ET.parse(xml_path).getroot()

    alumnos = []
    for a in root.findall(".//alumno"):
        raw_id = _pick(
            a,
            "id_alumno", "id", "nia", "NIA", "nie", "NIE", "documento", "DOCUMENTO", "identificador", "IDENTIFICADOR"
        )
        alumnos.append({
            "anyo": year_label,
            "id_alumno": sha256(raw_id),
            "fecha_nac": _pick(a, "fecha_nac", "fechaNacimiento", "fecha_nacimiento", "FECHA_NAC", "FECHA_NACIMIENTO"),
            "sexo": _pick(a, "sexo", "SEXO"),
            "estado_matricula": _pick(a, "estado_matricula", "ESTADO_MATRICULA"),
            "curso": _pick(a, "curso", "CURSO"),
            "grupo": _pick(a, "grupo", "GRUPO"),
            "turno": _pick(a, "turno", "TURNO"),
        })

    modulos = []
    for m in root.findall(".//contenido"):
        modulos.append({
            "anyo": year_label,
            "codigo": _pick(m, "codigo", "CODIGO", "id", "ID"),
            "nombre_cas": _pick(m, "nombre_cas", "NOMBRE_CAS", "nombre", "NOMBRE"),
            "curso": _pick(m, "curso", "CURSO"),
        })

    cursos = []
    for c in root.findall(".//curso"):
        cursos.append({
            "anyo": year_label,
            "codigo": _pick(c, "codigo", "CODIGO", "id", "ID"),
            "nombre_cas": _pick(c, "nombre_cas", "NOMBRE_CAS", "nombre", "NOMBRE"),
            "padre": _pick(c, "padre", "PADRE"),
        })

    califs = []
    for cal in root.findall(".//calificacion"):
        raw_al = _pick(cal, "alumno", "ALUMNO", "id_alumno", "ID_ALUMNO", "nia", "NIA", "nie", "NIE")
        califs.append({
            "anyo": year_label,
            "alumno": sha256(raw_al),  # ✅ para que case con alumnos.id_alumno
            "curso": _pick(cal, "curso", "CURSO"),
            "contenido": _pick(cal, "contenido", "CONTENIDO", "modulo", "MODULO", "codigo_modulo", "CODIGO_MODULO"),
            "nota_numerica": _pick(cal, "nota_numerica", "NOTA_NUMERICA", "nota", "NOTA"),
            "evaluacion": _pick(cal, "evaluacion", "EVALUACION"),
        })

    return alumnos, modulos, cursos, califs


def xml_to_bronze(xml_path: str, year_label: str, out_dir: str, **context):
    xml_path = Path(xml_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    alumnos, modulos, cursos, califs = _extract_tables_from_xml(xml_path, year_label)

    df_al = pd.DataFrame(alumnos).drop_duplicates()
    df_mo = pd.DataFrame(modulos).drop_duplicates()
    df_cu = pd.DataFrame(cursos).drop_duplicates()
    df_ca = pd.DataFrame(califs).drop_duplicates()

    df_al.to_csv(out_dir / f"alumnos_bronze_{year_label}.csv", index=False)
    df_mo.to_csv(out_dir / f"modulos_bronze_{year_label}.csv", index=False)
    df_cu.to_csv(out_dir / f"cursos_bronze_{year_label}.csv", index=False)
    df_ca.to_csv(out_dir / f"calificaciones_bronze_{year_label}.csv", index=False)

    log_event(
        dag_id=context["dag"].dag_id,
        task_id=context["task"].task_id,
        stage="BRONZE",
        status="SUCCESS",
        anyo=year_label,
        run_id=context.get("run_id"),
        logical_date=str(context.get("logical_date")),
        rows_alumnos=len(df_al),
        rows_modulos=len(df_mo),
        rows_cursos=len(df_cu),
        rows_calificaciones=len(df_ca),
        message=f"BRONZE generado desde XML: {xml_path.name} (IDs hasheados)",
    )
