

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
│   │       └── ...
│   ├── cursos/
│   │   ├── 2024-2025/
│   │   │   └── cursos.parquet
│   │   └── 2023-2024/
│   │       └── ...
│   ├── grupos/
│   │   ├── 2024-2025/
│   │   │   └── grupos.parquet
│   │   └── ...
│   ├── modulos/
│   │   ├── 2024-2025/
│   │   │   └── modulos.parquet
│   │   └── ...
│   └── calificaciones/
│       ├── 2024-2025/
│       │   ├── evaluation_1/
│       │   │   └── calificaciones_clean.parquet   
│       │   ├── evaluation_2/
│       │   └── evaluation_3/
│       └── 2023-2024/
│           └── ...
├── gold/
│   ├── kpi_ipc_0201_por_grupo/
 
```