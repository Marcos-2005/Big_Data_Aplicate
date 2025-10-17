***¿Cuál es el separador de columnas (coma , o punto y coma ; )?***

En todos los ficheros el separador es ,

***¿La primera fila contiene los nombres de las columnas (encabezados)? ¿Son claros?***

Si en todos los pone claros. Si están claros todos todos.

***Inspecciona visualmente las primeras 20-30 filas. ¿Ves valores que te parezcan extraños o que faltan (celdas vacías, "N/A", "s/d")?***

Si, en el archivo **Alumnos.csv** en municipio_nac salen algunas celdas en blanco. En provincia_nac en libro_escolaridad, cod_postal, expediente, ampa, dictamen, fecha_resolucion, informe_psicoped, informe_posib, tipo_matricula, num_repeticion  también hay datos en blanco.

En el archivo **Calificaciones.csv** la columna contenido está la mayoría con n´umeros del .

En el archivo **Cursos.csv** la columna padre está en blanco

En el archivo **Grupos.csv** la columna aula está en blanco

**Modulos.csv** y **Horas.csv** todo correcto.

***¿Los formatos son consistentes? Por ejemplo, ¿las fechas están siempre como DD/MM/AAAA o a veces cambian?***

Si son consistentes, el tipo de dato no cambia en la mayoría, pero en.

En el archivo **Calificaciones.csv** la columna bloque_contenido está en blanco.

En el archivo **Cursos.csv** la columna abreviatura está algunas filas con una cadena de números y en otras con numeros y letras.

En los archivos **Modulos.csv** y **Horas.csv** la columna codigo de las dos está la mayoría con números pero también en unas casillas tienen letras y numeros.

***Identifica las "claves" o "IDs" que podrían servir para relacionar unos ficheros con otros (ej: id_alumno en el fichero de calificaciones.csv y también en alumnos.csv ).***

En la tabla **Calificaciones.csv** tiene tres claves para hacer al dato único, el nia, el contenido y la evaluación.

**Alumnos.csv** se relaciona con **Calificaciones.csv** en la columna nia.Alumnos y la de alumnos.Calificaciones Y también se pueden ver por anyo.

**Alumnos.csv** se relaciona con **cursos.csv** en la columna curso.Alumnos y la de codigo.alumno Y también se pueden ver por anyo y fecha de exportacion.


**Cursos.csv** tiene dos columnas que tienen una relación ya que hay datos de curso.codigo que tiene el mismo valor que curso.padre, es una relación padre e hijo.

**Cursos.csv** se relaciona con **Calificaciones.csv** en la columna enseñanza.Cusos junto a codigo.Cursos y la de Calificaciones esenseñanza.Calificaciones junto a curso.Calificaciones.


La relación entre **Horas.csv** y **Modulos.csv** son las columnas código.Horas y la de codigo.Modulos. Y esto se confirma porque si ves que en las dos columnas de código pone el mismo código, verás que en las columnas NOMBRE_CAS.Horas y nombre_cas.mudulos sale el mismo nombre de la clase. Si en una tabla pone codigo 156 y ciclo Inglés en la otra tabla saldrá lo mismo codigo 156 nombre Inglés.

En la tabla **Alumnos.csv** la clave única es el NIA aunque también están los expediente que aunque sean clave unica no es la clave funcional de la tabla **Alumnos.csv**.

La relación entre **Grupos.txt** y **Cursos.txt** se establece mediante una coincidencia de la abreviatura del curso contenida en la columna nombre de Grupos.txt con la denominación completa del programa que aparece en las columnas nombre_cas o abreviatura de Cursos.txt ya que no existe una clave foránea explícita y directa entre ambas tablas en los datos proporcionados.