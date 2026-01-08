from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean


def crear_csv_ejemplo(input_csv: Path) -> str:
    input_csv.parent.mkdir(parents=True, exist_ok=True)

    if input_csv.exists():
        return str(input_csv)

    filas = [
        {"id_alumno": "1", "nombre": " ana  pÉrez ", "curso": "1SMR", "nota_1": "7,5", "nota_2": "8", "nota_3": "6"},
        {"id_alumno": "2", "nombre": "LUIS garcía", "curso": "1SMR", "nota_1": "4", "nota_2": "5,0", "nota_3": "4,5"},
        {"id_alumno": "3", "nombre": "María-luisa  lopez", "curso": "2SMR", "nota_1": "9", "nota_2": "8,5", "nota_3": "9,5"},
        {"id_alumno": "4", "nombre": "  joan  martín", "curso": "2SMR", "nota_1": "6", "nota_2": "6", "nota_3": "6"},
        {"id_alumno": "5", "nombre": "sara    nuñez", "curso": "1DAM", "nota_1": "3", "nota_2": "2,5", "nota_3": "4"},
        {"id_alumno": "6", "nombre": "Óscar romero", "curso": "1DAM", "nota_1": "5", "nota_2": "5", "nota_3": "5"},
        {"id_alumno": "7", "nombre": "laia  gÓmez", "curso": "2DAM", "nota_1": "8", "nota_2": "7,5", "nota_3": "8,5"},
        {"id_alumno": "8", "nombre": "PABLO SÁNCHEZ", "curso": "2DAM", "nota_1": "6,5", "nota_2": "6,0", "nota_3": "7"},
    ]

    with input_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id_alumno", "nombre", "curso", "nota_1", "nota_2", "nota_3"],
        )
        writer.writeheader()
        writer.writerows(filas)

    return str(input_csv)


def _to_float(nota_str: str) -> float:
    s = (nota_str or "").strip().replace(",", ".")
    return float(s)


def transformar_csv(input_csv: Path, output_csv: Path) -> dict:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    alumnos = []
    with input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre_limpio = " ".join((row["nombre"] or "").strip().split()).title()

            n1 = _to_float(row["nota_1"])
            n2 = _to_float(row["nota_2"])
            n3 = _to_float(row["nota_3"])
            media = round((n1 + n2 + n3) / 3, 2)
            aprobado = "SI" if media >= 5 else "NO"

            alumnos.append(
                {
                    "id_alumno": row["id_alumno"].strip(),
                    "nombre": nombre_limpio,
                    "curso": row["curso"].strip().upper(),
                    "nota_1": n1,
                    "nota_2": n2,
                    "nota_3": n3,
                    "media": media,
                    "aprobado": aprobado,
                }
            )

    alumnos.sort(key=lambda x: (x["curso"], -x["media"], x["nombre"]))

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id_alumno", "nombre", "curso", "nota_1", "nota_2", "nota_3", "media", "aprobado"],
        )
        writer.writeheader()
        writer.writerows(alumnos)

    return {"output_csv": str(output_csv), "n_registros": len(alumnos)}


def generar_resumen(output_csv: Path, summary_txt: Path) -> str:
    summary_txt.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    medias = [float(r["media"]) for r in rows] if rows else []
    aprobados = sum(1 for r in rows if r["aprobado"] == "SI")
    total = len(rows)
    top = sorted(rows, key=lambda r: float(r["media"]), reverse=True)[:3]

    with summary_txt.open("w", encoding="utf-8") as f:
        f.write("RESUMEN ALUMNOS Y NOTAS\n")
        f.write("======================\n\n")
        f.write(f"Total alumnos: {total}\n")
        f.write(f"Aprobados: {aprobados}\n")
        f.write(f"Suspendidos: {total - aprobados}\n")
        f.write(f"Media global: {round(mean(medias), 2) if medias else 'N/A'}\n\n")
        f.write("Top 3 por media:\n")
        for i, r in enumerate(top, start=1):
            f.write(f"  {i}. {r['nombre']} ({r['curso']}) - media {r['media']}\n")

    return str(summary_txt)
