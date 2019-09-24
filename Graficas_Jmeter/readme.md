# Manual de uso \[ [sourceCode](https://github.com/RafaelGB/pythonScripts/tree/master/Graficas_Jmeter) \]

La funcionalidad del script es ofrecer información y material gráfico sobre los parámetros CSV que se obtienen de la herramienta JMeter

## Parámetros contemplados

* `-f file` \[OBLIGATORIO\]  Seleciona el fichero CSV en su ruta relativa o absoluta.
* `-m mode`* *\[OBLIGATORIO\]
  * `**chunks**`: La información recogida del CSV se tratará por intervalos. Cada uno de ellos devolverá su resultado independiente. El tamaño de dichos intervalos es configurable.
  * `**full**`:   La información recogida del CSV se tratará en su conjunto, devolviendo un único resultado.
* `-o option` \[OBLIGATORIO\]
  * `**plotlyGraph**`: En función de la columna que se determine como marcaje (`--column nombreHeader`), Devuelve una gráfica de tiempos.
  * `**boxplot_seaborn**`: \[DEPRECATED\] devuelve una imagen con un boxplot de latencia sobre bytes enviados.
  * `**boxplot_plotly**`: Devuelve una interfaz con un boxplot de la columna x (`--colx`), columna y (`--coly`) indicadas por parámetro.
  * `**valores_unicos**`: Dado el nombre de una columna determinada como parámetro (`--column`), obtiene todos los valores únicos y el número de veces que aparecen.
  * `**system_metrics**`: Con las métricas obtenidas del sistema al que ataca JMeter (usando un agente), devuelve una gráfica con cada medida parametrizada (CPU, Memoria, NetworkIO,...)
* `-h` ó `--help`: muetra por consola el manual de uso