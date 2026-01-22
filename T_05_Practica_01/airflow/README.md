# Práctica 5.1 – Orquestación de un Pipeline de Análisis Académico con Apache Airflow

## Estructura de carpetas del proyecto

La organización del proyecto sigue una separación clara entre orquestación, código de transformación y capas de datos, alineada con la arquitectura Medallón:

```text
airflow/
├── dags/
│   ├── dag_datos.py              # DAG de ingesta (XML → Bronze)
│   ├── dag_limpiar.py            # DAG de limpieza y normalización (Bronze → Silver)
│   ├── dag_db.py                 # DAG de generación Gold y carga en MySQL
│   │
│   ├── include/                
│   │   ├── datos.py             
│   │   ├── limpiar.py           
│   │   ├── bd.py                 # Generación Gold y carga al Data Warehouse
│   │   └── logging_utils.py      # Registro de eventos en la tabla etl_log
│   │
│   ├── data/
│   │   └── ITACA/                # Datos de entrada (XML académicos)
│   │       ├── varios_23-24_anon.xml
│   │       ├── varios_23-24_anon_01.xml
│   │       ├── varios_23-24_anon_02.xml
│   │       ├── varios_24-25_anon.xml
│   │       ├── varios_24-25_anon_01.xml
│   │       ├── varios_24-25_anon_02.xml
│   │       └── varios_25-26_anon_01.xml
│   │
│   └── output/
│       ├── bronze/               # Capa Bronze (CSV crudos por año)
│       │   ├── alumnos_bronze_YYYY.csv
│       │   ├── cursos_bronze_YYYY.csv
│       │   ├── modulos_bronze_YYYY.csv
│       │   └── calificaciones_bronze_YYYY.csv
│       │
│       ├── silver/               # Capa Silver (CSV limpios)
│       │   ├── alumnos_silver_YYYY.csv
│       │   ├── cursos_silver_YYYY.csv
│       │   ├── modulos_silver_YYYY.csv
│       │   └── calificaciones_silver_YYYY.csv
│       │
│       └── gold/                 # Capa Gold (datos listos para explotación)
│           ├── alumnos_gold_YYYY.csv
│           ├── cursos_gold_YYYY.csv
│           ├── modulos_gold_YYYY.csv
│           └── calificaciones_gold_YYYY.csv
│
├── docker-compose.yaml           # Despliegue de Apache Airflow con Docker
└── README.md                     # Documentación del proyecto


## Arquitectura Medallón

El pipeline implementa una arquitectura Medallón clásica, donde cada capa tiene una responsabilidad clara:

```
data/ITACA (XML)
        ↓
output/bronze
        ↓
output/silver
        ↓
output/gold
        ↓
MySQL (Data Warehouse)
```

 **[TU_ARQUITECTURA_AQUÍ]**

###  Bronze – Datos crudos
- Conversión de XML a CSV.
- Separación por entidades y por año académico.
- Conservación fiel del dato de origen.

###  Silver – Datos limpios
- Eliminación de duplicados.
- Normalización de columnas.
- Eliminación de calificaciones asociadas a alumnos de baja.

###  Gold – Datos listos para explotación
- Datos alineados con el modelo del Data Warehouse.
- Tipos normalizados.
- Persistencia tanto en CSV como en MySQL.

---

## Flujo de Airflow (DAGs)

### `dag_datos` – Ingesta
- Detecta automáticamente los XML disponibles.
- Genera la capa Bronze.
- DAG programado diariamente.

### `dag_limpiar` – Transformación
- Limpia y normaliza datos.
- Genera la capa Silver.
- Se ejecuta automáticamente tras `dag_datos`.

### `dag_db` – Gold y carga
- Genera la capa Gold.
- Carga datos en MySQL.
- Registra métricas en la tabla `etl_log`.

---

## Ejecución diaria y mantenimiento

- Ejecución diaria automática mediante Airflow.
- Incorporación de nuevos XML sin cambios de código.
- Monitorización mediante logs y tabla `etl_log`.

---

## Verificación y resultados

Se adjuntan las siguientes evidencias:
- DAGs activos en Airflow.
- Ejecuciones exitosas.
- Logs de tareas.
- Consultas SQL a `etl_log`.

Ejemplo:
```sql
SELECT * FROM etl_log ORDER BY id DESC LIMIT 10;
```

---

## Conclusión

Este proyecto demuestra la evolución hacia un pipeline profesional, automatizado y mantenible, aplicando Apache Airflow y arquitectura Medallón en un entorno realista de ingeniería de datos.
