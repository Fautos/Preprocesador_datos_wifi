# Preprocesador_datos_wifi
Programa para realizar el preprocesado de los los datos wifi.
El principal funcionamiento de este programa es convertir un fichero csv en el que se registren las potencias de distintos puntos de acceso wifi que tenga la siguiente forma:

    | Punto 1 dentro de la muestra 1 | IDSS 1 | MAC 1 | Potencia 1 | Fecha 1 | Etiqueta (latitud-Longitud) 1 | Identificador 1 |
    | Punto 2 dentro de la muestra 1 | IDSS 2 | MAC 2 | Potencia 2 | Fecha 2 | Etiqueta (latitud-Longitud) 2 | Identificador 2 |
    | .............................. | ...... | ..... | .......... | ....... | ............................. | ............... |
    | Punto N dentro de la muestra 1 | IDSS N | MAC N | Potencia N | Fecha N | Etiqueta (latitud-Longitud) N | Identificador N |
    | Punto 1 dentro de la muestra 2 | IDSS M | MAC M | Potencia M | Fecha M | Etiqueta (latitud-Longitud) M | Identificador M |
    | .............................. | ...... | ..... | .......... | ....... | ............................. | ............... |
    | Punto X dentro de la muestra Y | IDSS X | MAC X | Potencia X | Fecha X | Etiqueta (latitud-Longitud) X | Identificador X |
    
En otro archivo csv en el que se organicen en función de la muestra, la potencia y la dirección MAC tal y como se muestra a continuación:
    
    |           |     MAC 1    |     MAC 2    |     MAC 3    | ... |     MAC N    | Etiqueta 1 (opc) | Etiqueta 2 (opc)  |
    | Muestra 1 | Potencia AP1 | Potencia AP2 | Potencia AP3 | ... | Potencia APN | Latitud muetra 1 | Longitud muetra 1 |
    | Muestra 2 | Potencia AP1 | Potencia AP2 | Potencia AP3 | ... | Potencia APN | Latitud muetra 2 | Longitud muetra 2 |
    | ......... | ............ | ............ | ............ | ... | ............ | ................ | ................. |
    | Muestra Y | Potencia APY | Potencia APY | Potencia APY | ... | Potencia APY | Latitud muetra Y | Longitud muetra Y |


## Como usarlo
Para lanzar el programa principal basta con pegarlo en la ubicación deseada y lanzarlo, por ejemplo con el siguiente comando:
    
    python3 Procesador_base_datos.py

El programa de testeo tiene el mismo modo de empleo, pero se ha de colocar en el mismo lugar que el principal (no dentro de una subcarpeta, para que no haya conflicto de direcciones). Para lanzarlo por ejemplo:

    python3 Tester_procesador.py

## Funcionamiento
Al lanzar por primera vez el programa se creará un arbol de carpetas en el lugar donde se localice dicho fichero. En las veces sucesivas buscará dicha carpeta, y de no encontrarla la creará de nuevo. En el caso de encontrar otra carpeta con el mismo nombre pero con contenido diferente esta será renombrada como "Database_antigua" para que se pueda conservar su contenido intacto.
Este arbol se organiza de la siguiente manera:
     
     |->Database
         |->Raw_data
             |->Train
             |->Test
             |->Val
         |->Processed_data
             |->Dia
                 |->Hora

En la carpeta "Raw_data" se introducirán los archivos csv que se quieran procesar. En la carpeta "Processed_data" se guardarán los archivos una vez procesados.

Dentro de la carpeta "Raw_data" se han de colocar los archivos en las carpetas correspondientes, los que queden fuera de ellas no seran procesados. Si se meten archivos en la carpeta "Train" estos serán utilizados para procesar el conjunto de entrenamiento, de igual manera si se meten en la carpeta "Tes" o "Val" se utilizarán para procesar los respectivos conjuntos.
Los datos se pueden introducir como .csv de manera individual o dentro de carpetas (o ambos a la vez). En caso de introducirlos como csv sueltos se ordenaran alfabéticamente, en caso de meter carpetas de por medio estas entrarán dentro de dicho orden (mirar el archivo "informacion.txt una vez finalice el programa).
Además de los archivos con los datos de las señales wifi se puede introducir una lista de direcciones MAC (nombrar como "listado") la cual servirá de referencia a la hora de ordenar los datos. Si no se introduce dicha lista los datos se ordenaran en orden creciente según su dirección MAC. Si se introduce dicha lista y entre los datos se encuentran direcciones MAC que no corresponden con ninguna de ellas estas se ubicarán al final o se eliminarán en función de lo que se indique, mirar apartado "Explicación de las variables".
En el caso de que haya datos en la carpeta de entrenamiento estos servirán de base para ordenar los datos de testeo y validación.

Finalmente en la carpeta "Processed_data" se guardarán todos los archivos extraidos del programa. Estos se localizan dentro de la carpeta que marca el día que se lanzó el programa, dentro de la carpeta con la hora respectiva.
Dependiendo de los datos procesados se obtendrán los siguientes ficheros (donde X corresponde con "Train", "Test" o "Val"):
* **matriz_X_organizada**: Este archivo contiene la matriz con los AP´s organizados tal y como se indica arriba.
* **matriz_X_etiquetas**: En caso de que se indique la separación de las etiquetas, y de haberlas, las mismas se exportarán en otro archivo (por defecto saldra, pero esto se puede cambiar desde el propio código). De lo contrario las etiquetas se posicionarán en las dos últimas columnas de "matriz_X_organizada.
* **matriz_X_timestamp**: Este archivo contiene las marcas temporales de las muestras, ordenadas de la misma forma que la matriz organizada.
* **listado_X**: En este fichero se encuentran las direcciones MAC que se han usado para organizar la matriz, por si se quiere reutilizar en futuros pre-procesados.
* **orden_X**: En este fichero se indican las direcciones de los archivos y el número de muestras de las que se compone cada uno. Es necesario para poder implementar el programa de testeo.
* **informacion**: Este fichero recoge información sobre el proceso. Puede resultar util a la hora de hacer comprobaciones.

## Explicación de las variables
Como hay varias alternativas a la hora de procesar los datos, se han colocado las variables en la parte de arriba del código para que el usuario pueda configurarlas a su gusto. A continuación encontrarás una descripción en detalle de cada una de ellas:

* **Espera**: Variable booleana para esperar tras la verificación del arbol de trabajo (para que se pueda ingresar los ficheros sin necesidad de reiniciar el programa) o si por el contrario no se quiere hacer la pausa (por motivos de fluidez).
* **Lista_exclusiones**: Es una lista con los nombres de las carpetas que no se quieren añadir al procesado. Por ejemplo, si dentro de la lista está el nombre "S7" en el caso de encontrar una carpeta así llamada en alguno de los directorios su contenido no se procesará.
* **max_directorios**: Indica el número máximos de directorios que se deben de tener en cuenta. La principal función de dicha variable es dar una opción de escape a un bucle while. Si hay menos carpetas que las indicadas no pasa nada, pero si hay más llegado al nivel indicado el programa parará (y por lo tanto los ficheros que esten dentro de las carpetas más abajo no se procesarán).
* **ordenar_listas**: Variablo booleana que indica si las listas de direcciones MACs se han de ordenar o no. En caso afirmativo se ordenarán en orden ascendente, en caso negativo se ordenarán según su orden de aparición (implica un tiempo extra).
* **junto_X**: Variable booleana que especifica si quieres obtener las etiquetes (en caso de haberlas) en la misma matriz de salida o si las quieres en un fichero aparte.
* **borrar_datos_nuevos**: Variable booleana que indica si quieres borrar los datos referentes a AP's solo vistos en los datos de Testeo y/o Validación o si los quieres conservar (en caso afirmativo aparecerán al final de la lista de AP's base).


## Programa de testeo
Además del programa principal se implementa también un programa de testeo, con el cual se puede verificar que la generación de la matriz haya sido la correcta. Para ello se ha de indicar dentro del mismo lo siguiente (en las variables que se localizan en las primeras líneas):
* **Conjunto**: Conjunto que se quiere testear, ya sea Train, Test o Val.
* **Nombre_fichero_original**: Dirección del fichero original (el que aportó os datos) a partir de la carpeta /Processed_data/Conjunto/... (por ejemplo, si queremos verificar un fichero que metimos directamente en la carpeta Train solo habría que poner su nombre, pero si dicho arcivo estuviese dentro de otra carpeta habría que poner "Otra_carpeta/Nombre_archivo").
* **Fecha** y **Hora**: Mirar en "Processed_data", y ponertal cual se indica en el arbol de arriba (son la fecha y la hora en la que se procesó la matriz).

El programa mostrará en el terminal si ha habido algún fallo, en cuyo caso indicará donde se ha localizado. Notesé además que si el fallo se debe a que se han encontrado dos direcciones MAC idénticas en la misma muestra lo comunicará, así como si el fallo se debe a que no se ha localizado la dirección AP (por ejemplo si le dijimos que borrase las que no apareciesen en el entrenamiento).

# Actualizaciones
## Actualización 16/09/2022
En esta actualización se han implementado varias mejoras, solucionado varios problemas y realizado cambios de calidad de vida:
* A partir de ahora es posible introducir los archivos .csv directamente desde carpetas.
* A partir de ahora se obtiene también un fichero aparte con las marcas temporales.
* Implementada una nueva opción para descartar los datos de AP's en los conjuntos de validación y testeo que no aparezcan en el listado original (o en el listado creado a partir de los datos de entrenamiento). 
* Ahora las variabes configurables aparecen en la primera línea, haciendolas más accesibles.
* Bugs arreglados:
    * Arreglado un fallo por el que antes los datos no se escribian correctamente cuando se introducían más de 2 ficheros.
    * Arreglado un bug por el cual ciertos archivos no se podía leer (por estar escritos en un formato erróneo) causando que el programa colapsase.

## Actualización 22/09/2022
En esta actualización se han realizado varias simplificaciones y mejoras, así como algún arreglo de bugs y se ha añadido una nueva funcionalidad:
* Se ha mejorado la información mostrada en el fichero "información.txt", mostrando ahora más datos.
* Se ha eliminado todo lo que tenía que ver con "Unlisted_data", tanto del código como de la información del programa, lo que ha llevado a una pequeña simplificación de código.
* Se ha añadido el fichero "orden_X" a los datos de salida.
* Se ha añadido el programa "Tester_procesador".
* Bugs arreglados:
    * Arreglado un fallo que hacía que los datos no se colocasen correctamente en las matrices de validación y testeo.

## Actualización 05/10/2022
En esta actualización se han corregido un par de errores y se ha implementado una nueva función:
* Se ha añadido la variable "ordenar_listas" con la que el usuario puede decidir si ordenar las MACs por aparación o por orden numérico.
* Bugs arreglados:
    * Arreglado un fallo por el que no se podían poner las etiquetas juntas en las matrices de testeo y validación.
    * Arreglado un fallo que hacía que no se generase el archivo "orden_Val".
