***¿Cuál es el separador de columnas (coma , o punto y coma ; )?***

En todos los ficheros el separador es , exceptoIndicadores Finales que es ;

***¿La primera fila contiene los nombres de las columnas (encabezados)? ¿Son claros?***

Si en todos los pone claros. Si están claros todos todos.

***Inspecciona visualmente las primeras 20-30 filas. ¿Ves valores que te parezcan extraños o que faltan (celdas vacías, "N/A", "s/d")?***

No se observan valores faltantes o extraños. Todos los códigos de proceso y sus descripciones están presentes, expecto en **Indicadores_Finales** que se observan espacios en blanco que es que faltan valores, como Cod_SQ y Cod_PAA


**Modulos.csv** y **Horas.csv** todo correcto.

***¿Los formatos son consistentes? Por ejemplo, ¿las fechas están siempre como DD/MM/AAAA o a veces cambian?***

En **Lineas** los formatos son consistentes. La columna Linea utiliza identificadores numéricos simples (1, 2, 3, etc.) y la columna Descripcion_Linea contiene texto descriptivo. 

En **Objetivos** los formatos son consistentes. La columna Objetivo_PAA utiliza un formato alfanumérico (ej. 1A, 1B, 2A). La columna Linea utiliza un formato numérico simple. 

En **Procesos** Los formatos son consistentes. La columna Proceso utiliza un formato alfanumérico estandarizado (PC01, PS01, PE01) y la descripción es texto.

En **Indicadores_Finales**  La columna Curso utiliza un formato consistente YYYY/YY. Pero existe una inconsistencia en el formato de los separadores decimales: la mayoría de los valores utilizan la coma (,) como separador decimal pero hay al menos dos casos en los que se utiliza el punto . como separador decimal (52.02 y 75.6 que haya podido ver yo).

***Identifica las "claves" o "IDs" que podrían servir para relacionar unos ficheros con otros (ej: id_alumno en el fichero de calificaciones.csv y también en alumnos.csv ).***

**Lineas**

PK linea 
FK no hay

**Objetivos**

PK objetivo_PAA 
FK linea que proviene de Lineas

**Procesos**

PK proceso 
FK no hay

**Indicadores_Finales**

PK  Curso, Identificador, Indicador (Clave compuesta) 
FK cod_PAA que proviene de un conjunto de Objetivos y Lineas
FK Cod_SQ que proviene de un conjunto de Proceso y Lineas
