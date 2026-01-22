# Práctica 5.1 – Orquestación de un Pipeline de Análisis Académico con Apache Airflow

## Contexto y evolución del proyecto (Storyboard técnico)

Este proyecto nace como una evolución natural del flujo de **Análisis Académico** desarrollado previamente con **Apache NiFi**. En aquella primera aproximación, el objetivo principal era comprender el flujo de datos y validar la viabilidad del procesamiento de información académica (alumnos, cursos, módulos y calificaciones) a partir de ficheros XML.

Con la introducción de **Apache Airflow**, el planteamiento cambia: pasamos de un flujo principalmente visual y manual a un **pipeline completamente orquestado, reproducible y automatizado**, siguiendo buenas prácticas de ingeniería de datos.

Las decisiones clave de diseño han sido:
- Separar claramente cada etapa del procesamiento.
- Adoptar una **arquitectura Medallón (Bronze / Silver / Gold)** para mejorar trazabilidad y calidad del dato.
- Centralizar la orquestación en Airflow, usando código Python en lugar de herramientas visuales.
- Preparar el sistema para **ejecución diaria**, permitiendo la incorporación de nuevos ficheros XML sin modificar el código.

El resultado es un pipeline robusto, escalable y alineado con escenarios reales de Data Engineering.

---

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

📌 **[TU_ARQUITECTURA_AQUÍ]**

### 🥉 Bronze – Datos crudos
- Conversión de XML a CSV.
- Separación por entidades y por año académico.
- Conservación fiel del dato de origen.

### 🥈 Silver – Datos limpios
- Eliminación de duplicados.
- Normalización de columnas.
- Eliminación de calificaciones asociadas a alumnos de baja.

### 🥇 Gold – Datos listos para explotación
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
