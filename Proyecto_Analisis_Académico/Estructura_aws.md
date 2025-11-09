

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
academico-data-lake/
├── gold/
│   ├── kpi_ipc_0201_por_grupo/
│   │   ├── 2024-2025/
│   │   │   ├── evaluation_1/
│   │   │   │   └── ipc_0201_grupos.parquet      
│   │   │   ├── evaluation_2/
│   │   │   └── evaluation_3/
│   │   └── 2023-2024/
│   │       └── etc...
│
│   ├── kpi_ipc_0201_por_curso_anual/
│   │   ├── 2024-2025/
│   │   │   └── ipc_0201_anual.parquet          
│   │   └── 2023-2024/
│       └── etc...
│
│   └── kpi_ipc_0201_historico/
│       ├── 2018-2019_to_2024-2025/
│       │   └── ipc_0201_trend.parquet           
│       └── etc...

```