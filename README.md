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
    

Al lanzar por primera vez el programa se creará un arbol de carpetas en el lugar donde se localice dicho fichero. En las veces sucesivas buscará dicha carpeta, y de no encontrarla la creará de nuevo. En el caso de encontrar otra carpeta con el mismo nombre pero con contenido diferente esta será renombrada como "Database_antigua" para que se pueda conservar su contenido intacto.
Este arbol se organiza de la siguiente manera:
     
     |->Database
         |->Raw_data
             |->Unlisted_data (*)Funcionamiento no implementado, por favor dejar vacía.
             |->Train
             |->Test
             |->Val
         |->Processed_data
             |->Dia
                 |->Hora

En la carpeta "Raw_data" se introducirán los archivos csv que se quieran procesar. En la carpeta "Processed_data" se guardarán los archivos una vez procesados.
Dentro de la carpeta "Raw_data" se han de colocar los archivos en las carpetas correspondientes, los que queden fuera de ellas no seran procesados. Si se meten archivos en la carpeta "Train" estos serán utilizados para procesar el conjunto de entrenamiento, de igual manera si se meten en la carpeta "Tes" o "Val" se utilizarán para procesar los respectivos conjuntos.
Además de los archivos con los datos de las señales wifi se puede introducir una lista de direcciones MAC (nombrar como "listado") la cual servirá de referencia a la hora de ordenar los datos. Si no se introduce dicha lista los datos se ordenaran en orden creciente según su dirección MAC. Si se introduce dicha lista y entre los datos se encuentran direcciones MAC que no corresponden con ninguna de ellas estas se ubicarán al final.
En el caso de que haya datos en la carpeta de entrenamiento estos servirán de base para ordenar los datos de testeo y validación.

Finalmente en la carpeta "Processed_data" se guardarán todos los archivos extraidos del programa. Estos se localizan dentro de la carpeta que marca el día que se lanzó el programa, dentro de la carpeta con la hora respectiva.
Dependiendo de los datos procesados se obtendrán los siguientes ficheros (donde X corresponde con "Train", "Test" o "Val"):
* matriz_X_organizada: Este archivo contiene la matriz con los AP´s organizados tal y como se indica arriba.
* matriz_X_etiquetas: En caso de que se indique la separación de las etiquetas, y de haberlas, las mismas se exportarán en otro archivo (por defecto saldra, pero esto se puede cambiar desde el propio código). De lo contrario las etiquetas se posicionarán en las dos últimas columnas de "matriz_X_organizada.
* listado_X: En este fichero se encuentran las direcciones MAC que se han usado para organizar la matriz, por si se quiere reutilizar en futuros pre-procesados.
* informacio: Este fichero recoge información sobre el proceso. Puede resultar util a la hora de hacer comprobaciones.
