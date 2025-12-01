

```bash
academico-data-lake/
├── bronze/                                      # Datos crudos
│   ├── 2024-2025/                               
│   │   ├── evaluation_1/
│   │   │   ├── Alumnos_raw.csv
│   │   │   ├── Calificaciones_raw.csv
│   │   │   ├── Cursos_raw.csv
│   │   │   ├── Grupos_raw.csv
│   │   │   └── Modulos_raw.csv
│   │   ├── evaluation_2/
│   │   │   ├── Alumnos_raw.csv
│   │   │   └── etc..
│   │   └── evaluation=03/
│   │       └── etc...
│   ├── 2023-2024/
│   │   └── evaluation_1/
│   │       └── etc...
│   └── 2018-2019/
│        └── evaluation_1/
│           └── etc...
│
├── silver/                                      
│   ├── alumnos/
│   │   ├── 2024-2025/
│   │   │   └── alumnos.parquet
│   │   └── 2023-2024/
│   │       └── etc...
│   ├── cursos/
│   │   ├── 2024-2025/
│   │   │   └── cursos.parquet
│   │   └── 2023-2024/
│   │       └── etc...
│   ├── grupos/
│   │   ├── 2024-2025/
│   │   │   └── grupos.parquet
│   │   └── etc...
│   ├── modulos/
│   │   ├── 2024-2025/
│   │   │   └── modulos.parquet
│   │   └── etc...
│   └── calificaciones/
│       ├── 2024-2025/
│       │   ├── evaluation_1/
│       │   │   └── calificaciones_clean.parquet   
│       │   ├── evaluation_2/
│       │   └── evaluation_3/
│       └── 2023-2024/
│           └── etc...
├── gold/
│   ├── resultados_por_grupo/
│   │   ├── 2024-2025/
│   │   │   ├── evaluation_1/
│   │   │   │   └── resumen_grupos.parquet      
│   │   │   ├── evaluation_2/
│   │   │   └── evaluation_3/
│   │   └── 2023-2024/
│   │       └── etc...
│
│   ├── resultados_por_curso/
│   │   ├── 2024-2025/
│   │   │   └── resumen_curso.parquet          
│   │   └── 2023-2024/
│       └── etc...
│
│   └── evolucion_centro/
│       ├── 2018-2019_to_2024-2025/
│       │   └── evolucion.parquet           
│       └── etc...

```