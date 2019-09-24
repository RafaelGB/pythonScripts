# Manual de uso \[ [sourceCode](https://github.com/RafaelGB/pythonScripts/tree/master/Graficas_Jmeter) \]

La funcionalidad del script es ofrecer información y material gráfico sobre los parámetros CSV que se obtienen de la herramienta JMeter

## Parámetros contemplados

* `-m %mode%`* *\[OBLIGATORIO\]
  * `**chunks **`: La información recogida del CSV se tratará por intervalos. Cada uno de ellos devolverá su resultado independiente. El tamaño de dichos intervalos es configurable.
  * `**full **`:   La información recogida del CSV se tratará en su conjunto, devolviendo un único resultado