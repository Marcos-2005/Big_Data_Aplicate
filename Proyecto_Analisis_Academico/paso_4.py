import os
import pandas as pd

# Base del proyecto (carpeta donde está este script)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Carpetas de origen y destino
folders = [
    ("Indicadores", "Indicadores_parquet"),
    ("Datos_2022", "Datos_2022_parquet"),
]

for input_folder, output_folder in folders:
    input_path = os.path.join(base_dir, input_folder)
    output_path = os.path.join(base_dir, output_folder)

    # Crear carpeta de salida si no existe
    os.makedirs(output_path, exist_ok=True)

    print(f"\n Procesando carpeta: {input_folder}")

    # Recorre todos los CSV dentro de la carpeta
    for file in os.listdir(input_path):
        if file.endswith(".csv"):
            csv_file = os.path.join(input_path, file)
            parquet_file = os.path.join(output_path, file.replace(".csv", ".parquet"))

            try:
                # Leer el CSV (detectando el separador automáticamente)
                df = pd.read_csv(csv_file, sep=None, engine="python", on_bad_lines="warn")

                # Convertir a Parquet
                df.to_parquet(parquet_file, engine="pyarrow")

                print(f" Convertido: {file} → {os.path.basename(parquet_file)}")

            except Exception as e:
                print(f" Error con {file}: {e}")

print("\ Conversión completada con éxito para todas las carpetas.")
