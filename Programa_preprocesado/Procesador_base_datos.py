#!/usr/bin/env python
# coding: utf-8

# En los apartados marcados con (*) se puede leer más información desde el Readme del repositorio de GitHub o desde el archivo Jupyter. Aquí se han acotado para reducir el tamaño del programa (en líneas) 

# ## Librerías
#Para gestionar el directorio
import os
import time

#Para filtrar los datos
import pandas as pd
import re
import numpy as np

# ## Definición de variables (*)

#Para el inicio
Espera = False

#Para la extracción de ficheros
#Lista con los nombre de los directorios que se quieran excluir
Lista_exclusiones=[
    "S7"
]

#Número máximo de directorios que puede abrir antes de parar
max_directorios = 5

#Variable para indicar si se busca ordenar las lista de APs al crear la matriz o si se forman conforma vayan saliendo
ordenar_listas=False #False= bucle for, True=np.uniques

#Para la obtención de las matrices
#Definimos si queremos las etiquetas en la misma matriz que los datos o por separado y si queremos borrar los datos que no aparezcan en la lista
junto_Train = True
junto_Test = True
junto_Val = True

#Para añadir la columna de tiempo a la matriz de salida
add_timestamp = True

#Definimos si queremos eliminar o conservar los datos que hagan referencia a AP's que solo se encuentren en los ficheros de validación y testeo
borrar_datos_nuevos_Test = True
borrar_datos_nuevos_Val = True

#Variable para lanzar el checkeo del valor mínimo
check_minimun = False

#Valor por el que se reempplazarán las potencias que no se vean
inv_value=-100

# ## Creación del espacio de trabajo (*)

#Función para crear las carpetas a partir de una lista de direcciones
def Crea_directorios(lista):
  for direccion in lista:
    os.mkdir(direccion)

#Definimos todas las direcciones necesarias.
current_path = os.getcwd()
external_path = current_path + "/Database"

raw_path = external_path + "/Raw_data"
raw_train_path = raw_path + "/Train"
raw_test_path = raw_path + "/Test"
raw_val_path = raw_path + "/Val"

#Y las direcciones de los archivos de salida
processed_path = external_path + "/Processed_data"
str_date = str(time.gmtime().tm_mday)+"_"+str(time.gmtime().tm_mon)+"_"+str(time.gmtime().tm_year)
str_hour = str(time.gmtime().tm_hour)+":"+str(time.gmtime().tm_min)+":"+str(time.gmtime().tm_sec)
date_path = processed_path + "/" + str_date
hour_path = date_path + "/" + str_hour

#Para la informacion
str_info = ("Información sobre el procesado de datos ejecutado el día " + str(str_date) + " a las " +str(str_hour) +".\n")

lista_direcciones=[external_path,raw_path,raw_train_path,raw_test_path,raw_val_path,processed_path]

#Primero comprobamos si existe la carpeta adecuada. 
if(os.path.exists(external_path)):
    print("Encontrada la carpeta 'Database'. Procedemos a verificar que es la adecuada.")
    if(os.path.exists(raw_path) & os.path.exists(processed_path)):
        if(os.path.exists(raw_train_path) & os.path.exists(raw_test_path) & os.path.exists(raw_val_path)):
            print('\033[1mCarpeta identificada con éxito.\033[0m')
        else:
            print("Parece que hay un error. El arbol de trabajo es incorrecto, lo cual podría indicar que la carpeta 'Database' fue creada con otro fin. Procedo a cambiarla el nombre a 'Database_antigua' y creo un nuevo directorio con la configuración adecuada.")
            os.rename(external_path, external_path+'_antigua_' + str(time.time()))
            Crea_directorios(lista_direcciones)
            
    else:
        print("Parece que hay un error. El arbol de trabajo es incorrecto, lo cual podría indicar que la carpeta 'Database' fue creada con otro fin. Procedo a cambiarla el nombre a 'Database_antigua' y creo un nuevo directorio con la configuración adecuada.")
        os.rename(external_path, external_path+'_antigua_' + str(time.time()))
        Crea_directorios(lista_direcciones)

else:
    print("No se ha encontrado la carpeta 'Database'. Se procede a crear todos los directorios.")
    Crea_directorios(lista_direcciones)    
    print("El arbol de trabajo ya ha sido creado.")
    
print("\033[1m[info]\033[0m: Por favor, diríjase a la dirección: '"+ str(external_path) +"' e ingrese los archivos .csv en la carpeta 'Raw_data' para continuar.")
print("Dentro de esa carpeta encontrará varias opciones, coloque los .csv en las carpetas de las que quiera crear un conjunto.")
print("Por ejemplo, si ingresa 2 archivos en la carpeta 'Train' ambos se procesaran como datos de entrenamiento, y si además mete otro dos en la carpeta 'Test' estos archivos se procesaran aparte en un conjunto de testeo.")
print("\033[1m[info]\033[0m: También puede meter un listado base con los AP's conforme los quieras colocar. Los datos se procesaran teniendo en cuenta esa lista.")
print("\033[1m[importante]\033[0m: Si quieres meter un listado en alguna carpeta asegurate de que este contenga el nombre 'listado'.")
print("\033[1m[info]\033[0m: Los archivos que queden fuera de alguna de estas carpetas no seran procesados.")

if(Espera):
    #Creamos una espera por si no se han metido los datos
    input("Cuando tengas todo listo pulsa el botón \033[1m'Enter'\033[0m y procederemos con el procesado de los datos.")

# Empezamos a contar para saber cuanto tardamos en ejecutar el programa
tiempo_inicio = time.time()


# ## Obtención de los datos (*)
# Carga de datos

#Función para diferenciar los ficheros y carpetas de una lista de direcciones 
def Encuentra_ficheros(lista_direcciones):
    #La función ha de generar una lista con las direcciones de los ficheros a apartir de una dirección de un nivel superior
    Lista_ficheros = []
    Lista_directorios = []

    for direccion in lista_direcciones:
        #print(direccion)
    
        if os.path.isdir(direccion): 
            Lista_directorios.append(direccion)
            #print("Encontrado directorio.")

        else:
            Lista_ficheros.append(direccion)
    
    return Lista_ficheros, Lista_directorios

Lista_raw_path=[
    "raw_train_path",
    "raw_test_path",
    "raw_val_path"
]

str_info = str_info + "\n\u25BA Registro de ficheros \u25C4\n"

#Recorremos la lista de direcciones 
for path in Lista_raw_path:
    #Guardamos el nombre del conjunto (Train, Test, etc)
    conjunto =  path[4].upper() + path[5:-5]
    
    #Si está vacio no hacemos nada, pero llevamos la cuenta para asegurar de que al menos una carpeta contenga algo
    if(len(os.listdir(globals()["%s" % path]))==0):
        print("La carpeta '\033[1m"+str(conjunto)+"\033[0m' esta vacia.")
        
    #Si tiene algo en su interior analizamos que clase de elemento es
    else:
        print("Se han encontrado los siguientes archivos en la carpeta '\033[1m"+str(conjunto)+"\033[0m':")
        str_info = str_info +"Se han extraido datos de los siguientes archivos localizados en la carpeta "+str(conjunto)+":\n"
        
        #Inicializamos la matriz donde almacenaremos las direcciones de los archivos
        globals()['direcciones_%s' % conjunto]=[]
        
        for elemento in os.listdir(globals()["%s" % path]):
            
            #Nos aseguramos que el elemento no pertenezca a la lista de exclusiones
            if(elemento not in Lista_exclusiones):
                path_elemento = globals()["%s" % path] + "/" + elemento

                #Si el elemento es un fichero
                if os.path.isdir(path_elemento)== False:
                    globals()['direcciones_%s' % conjunto] += [path_elemento]

                    print("\t \u23FADocumento: " +str(elemento))
                    str_info = str_info + "\t \u23FADocumento: " +str(elemento) +"\n"

                else:
                    #Primero buscamos los ficheros desde el nivel superior
                    Lista_superior = [path_elemento +"/" + files for files in os.listdir(path_elemento)]
                    Lista_ficheros, Lista_directorios = Encuentra_ficheros(Lista_superior)
  
                    print("\t \u23FACarpeta: " +str(elemento) +" formada por "+str(len(Lista_ficheros))+" ficheros y "+str(len(Lista_directorios))+" subcarpetas.")
                    str_info=str_info + "\t \u23FACarpeta: " +str(elemento) +" formada por "+str(len(Lista_ficheros))+" ficheros y "+str(len(Lista_directorios))+" subcarpetas.\n"
                    
                    #En caso de encontrarnos con directorios en los niveles inferiores vamos bajando hasta sacar todos los ficheros
                    contador = 0
                    start_str = "\t \u23FA"
                    str_sub=""
                    while((len(Lista_directorios)!=0) and (contador <= max_directorios)):
                        
                        start_str = "\t"+start_str
                        str_sub = "sub-"+str_sub
                        lis_direc=[]
                        lis_fic=[]

                        for direc in Lista_directorios:
                            
                            if(str(direc.split("/")[-1]) not in Lista_exclusiones):
                                print(start_str + "Dentro de la carpeta "+str(direc.split("/")[-2])+" se encuentra la "+str_sub+"carpeta "+str(direc.split("/")[-1])+" que contenía "+str(len(os.listdir(direc)))+" elementos.")
                                str_info=str_info + start_str + "Dentro de la carpeta "+str(direc.split("/")[-2])+" se encuentra la "+str_sub+"carpeta "+str(direc.split("/")[-1])+" que contenía "+str(len(os.listdir(direc)))+" elementos.\n"
                                
                                lis_direc+=[direc + "/" + str(fichero) for fichero in os.listdir(direc)]
                            
                            else:
                                print(start_str +"[Exclusión]: Dentro de la carpeta "+str(direc.split("/")[-2])+" se encuentra la "+str_sub+"carpeta "+str(direc.split("/")[-1])+" que pertenece a la lista de exclusión, por lo que no será procesada.\n")
                                str_info=str_info + start_str + "[Exclusión]: Dentro de la carpeta "+str(direc.split("/")[-2])+" se encuentra la "+str_sub+"carpeta "+str(direc.split("/")[-1])+" que pertenece a la lista de exclusión, por lo que no será procesada.\n"
                        
                        lis_fic, Lista_directorios = Encuentra_ficheros(lis_direc)
                        if(len(lis_fic)!=0):
                            Lista_ficheros = Lista_ficheros + lis_fic

                        contador = contador +1

                    globals()['direcciones_%s' % conjunto] += Lista_ficheros

            else:
                print("\t \u23FAEl elemento "+ str(element)+" se encuentra dentro de la lista de exclusiones, por lo que no se procesará.")
                str_info=str_info +"\t \u23FAEl elemento "+ str(element)+" se encuentra dentro de la lista de exclusiones, por lo que no se procesará.\n"
           
    if('direcciones_'+ str(conjunto) in globals()):
        globals()['direcciones_%s' % conjunto] = sorted(globals()['direcciones_%s' % conjunto])
    
assert (("direcciones_Train" in globals()) or ("direcciones_Test" in globals()) or ("direcciones_Val" in globals())), "[\033[1mImportante\033[0m]: No se ha encontrado ninguna archivo que procesar. Por favor, introduzca algún archivo y verifique que este no pertenezca a la lista de exclusiones."

# Función para sacar las matrices (*)
def Saca_matrices(direcciones):
    #Almacenaremos los datos en una lista de listas de tamaño variable en función de la cantidad de ficheros que haya
    datos_totales=[]
    secuencias=[]
    listado = None
    orden=[]
    
    #Para cargar los datos usamos pd.read_csv(), el cual nos carga los datos en formato Dataframe, pero nosotros lo convertiremos a lista para poder trabajar con ello
    for direccion in direcciones:
        #Comprobamos que no sea un archivo de listado
        if("listado" in direccion):
            listado = pd.read_csv(direccion, header = None).to_numpy()[1:]
            listado = np.array([item for sublist in listado for item in sublist])
            print("[Importante]: Se ha encontrado una lista base")
            globals()["str_info"]=globals()["str_info"] + "[Importante]: Se ha encontrado una lista base\n"
        else:
            print(direccion)
            datos_totales.append((pd.read_csv(direccion, on_bad_lines='skip', header = None)).to_numpy().tolist())
    
    #Mostramos la cantidad de datos que se han leido para asegurarnos más tarde de que no se pierda ninguno
    print("En total se han descargado "+ str(len(datos_totales)) +" ficheros, los cuales se colocarán siguiendo el orden que se muestra a continuación:")
    globals()["str_info"]=globals()["str_info"] + "En total se han descargado "+ str(len(datos_totales)) +" ficheros, los cuales tienen las siguientes dimensiones:\n"
    
    cuenta_datos = 0
    for i in range(len(datos_totales)):
        print("El archivo '"+ str(direcciones[i]) +" contenía "+ str(len(datos_totales[i])) +" datos.")
        print("En total representaban "+str(datos_totales[i][-1][0])+" secuencias.")
        globals()["str_info"]=globals()["str_info"] + "\t\u23FA" + "El archivo '"+ str(direcciones[i]) +" contenía "+ str(len(datos_totales[i])) +" datos, los cuales en total representaban "+str(datos_totales[i][-1][0] +1)+" secuencias.\n"
        cuenta_datos = cuenta_datos + len(datos_totales[i])
        secuencias.append(datos_totales[i][-1][0])
        orden.append([str(direcciones[i]), datos_totales[i][-1][0]])
        
    print("Por lo que el total de datos a procesar tiene que ser de "+str(cuenta_datos))
    
    #Una vez cargados los datos los pasaremos de una lista de listas a una sola lista
    flat_list = [item for sublist in datos_totales for item in sublist]
    print("Al realizar el 'aplanamiento' nos quedamos con un total de "+ str(len(flat_list)))
    assert len(flat_list) == cuenta_datos, "Ha surgido un error al aplanar los datos. Originalmente había "+ str(cuenta_datos) +", pero tras aplanar nos hemos quedado con "+ str(len(flat_list)) +".Por favor, revisa el código"
    
    #Escribimos más informacion
    globals()["str_info"]=globals()["str_info"] + "El total de datos a procesar dentro de este conjunto ha de ser de "+str(cuenta_datos)+ " contenidos en "+str(sum(secuencias)+len(secuencias))+" secuencias.\n"
    
    #Finalmente convertimos dicha lista a formato matriz para poder trabajar con ella de manera cómoda
    matriz = np.array(flat_list)
    
    return matriz, secuencias, listado, orden

#Creamos las listas de entrenamiento, testeo y validación
if("direcciones_Train" in globals()):
    print('\033[1m'+'Set de entrenamiento'+'\033[0m')
    str_info = str_info + "\n\u25BA Extracción de datos del set de entrenamiento \u25C4\n"
    matriz_Train, secuencias_Train, listado_base_Train, orden_Train = Saca_matrices(direcciones_Train)
    print("Se ha creado la variable matriz_Train")
    
else:
    if("matriz_Train" in globals()): del matriz_Train
    if("secuencias_Train" in globals()): del secuencias_Train
    if("listado_base_Train" in globals()): del listado_base_Train
    if("orden_Train" in globals()):del orden_Train

if("direcciones_Test" in globals()):
    print('\033[1m'+'Set de testeo'+'\033[0m')
    str_info = str_info + "\n\u25BA Extracción de datos del set de testeo \u25C4\n"
    matriz_Test, secuencias_Test, listado_base_Test, orden_Test = Saca_matrices(direcciones_Test)
    print("Se ha creado la variable matriz_Test")
else:
    if("matriz_Test" in globals()): del matriz_Test
    if("secuencias_Test" in globals()): del secuencias_Test
    if("listado_base_Test" in globals()): del listado_base_Test
    if("orden_Test" in globals()):del orden_Test
        
if("direcciones_Val" in globals()):
    print('\033[1m'+'Set de validación'+'\033[0m')
    str_info = str_info + "\n\u25BA Extracción de datos del set de validación \u25C4\n"
    matriz_Val, secuencias_Val, listado_base_Val, orden_Val = Saca_matrices(direcciones_Val)
    print("Se ha creado la variable matriz_Val")
else:
    if("matriz_Val" in globals()): del matriz_Val
    if("secuencias_Val" in globals()): del secuencias_Val
    if("listado_base_Val" in globals()): del listado_base_Val
    if("orden_Val" in globals()):del orden_Val
        
#Recuento del tiempo
tiempo_datos = time.time()
tiempo_total = tiempo_datos-tiempo_inicio

segundos=tiempo_total
 
horas=int(segundos/3600)
segundos-=horas*3600
minutos=int(segundos/60)
segundos-=int(minutos*60)
segundos =int(segundos)

print("\n\u23F3%s:%s:%s" % (horas,minutos,segundos))
str_info = str_info + "\n\t\u23F3 En total el proceso de extracción de datos ha tardado " + str(horas) +":"+str(minutos)+":"+str(segundos)+".\n"

# ## Procesado de los datos(*)
#Comprobamos si hay alguna lista y limpiamos las que haya (si tienen indices Latitud o Longitud los eliminamos)
lista_listas=[
    "listado_base_Train",
    "listado_base_Test",
    "listado_base_Val"
]

lista_filtros=[
    "Latitud",
    "Longitud"
]

str_info = str_info + "\n\u25BA Obtención de las listas \u25C4\n"

for element in lista_listas:
    if((element in globals()) & (element is not None)):
        print("Se ha encontrado la lista: "+str(element))
        if (globals()['%s' % element] is None):
            print("El elemento estaba vacio, así que pasamos a borrarlo")
            del (globals()['%s' % element])
        else:
            print("La lista está formada por " +str(len(globals()['%s' % element]))+ " APs. Mostramos las primeras 10 filas de la lista:\n" +str(globals()['%s' % element][0:10]))
            str_info = str_info + "Se ha encontrado la lista: "+str(element) + " formada por " +str(len(globals()['%s' % element]))+ " APs. Mostramos las primeras 10 filas de la lista:\n" +str(globals()['%s' % element][0:10]) +"\n"
            
            #Revisamos que no haya columnas "Latitud" o "Longitud"
            for filtro in lista_filtros:     
                if(filtro in globals()["%s"%element]):
                    #print("Encontrada columna "+filtro+" en " + element + ". Procedemos a borrarla.")
                    posicion = np.where(globals()["%s"%element]==filtro)[0][0]
                    #print(posicion)
                    globals()["%s"%element]=np.delete(globals()["%s"%element], posicion)
                    print("En la lista original se encontraron columnas que sobran ('Latitud o Longitud'), tras borrarlas nos quedamos con una lista base de tamaño "+ str(len(globals()["%s"%element])))
                    str_info = str_info + "En la lista original se encontraron columnas que sobran ('Latitud o Longitud'), tras borrarlas nos quedamos con una lista base de tamaño "+ str(len(globals()["%s"%element]))
                    
if("matriz_Train" in globals()):
    if("listado_base_Train" not in globals()):
        #Filtramos en función de las direcciones MAC, las cuales se presentan en la 3 columna
        matriz_Aps = np.zeros(matriz_Train.shape[0])
        matriz_Aps = matriz_Train[:,2]

        #Nos quedamos solo con uno de cada para crear la lista
        if(ordenar_listas==False):
            #Si no queremos ordenar la lista mostramos las direcciones MAC conforme vayan apareciendo
            print("Como ha seleccionado la opción para no ordenar la lista, se esta procesando usando un bucle for, por lo que este paso puede tomar un poco de tiempo.")
            Aps_unicos = []            
            for element in matriz_Aps:
                if element not in Aps_unicos: Aps_unicos.append(element)
            Aps_unicos=np.array(Aps_unicos)
            str_info = str_info + "El listado con las direcciones MAC se ha procesado manualmente ya que ha seleccionado la opción de no ordenarlo."
            
        else:
            Aps_unicos = np.unique(matriz_Aps)    
            str_info = str_info + "El listado ha sido ordenado de forma ascendente en función de las direcciones MAC."
            
        print("Entre los datos de entrenamiento se han encontrado un total de "+ str(len(Aps_unicos))+" direcciones MAC diferentes. \nAquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) )
        listado_base_Train = Aps_unicos
        
        str_info = str_info + "Hemos procesado los datos de entrenamiento. En total hemos detectado " +str(len(Aps_unicos))+" direcciones MAC únicas." + "Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) + "\n"


# ##Funciónes para ordenar los datos (*)
def Organizador_entrenamiento(matriz_scan, secuencias, identificadores, etiquetas_juntas=False, add_time=False):
    #En la primera columna de la matriz se almacena el número de escaneo, así que para saber cuantos escaneos hay leemos el valor de la primera columna de la última fila
    numero_scaneos=sum(secuencias)+len(secuencias) #Como empiezan en 0 sumamos 1 por cada secuencia
    print("Localizados "+str(numero_scaneos)+" escaneos distintos")
    globals()["str_info"]=globals()["str_info"] + "Localizados "+str(numero_scaneos)+" escaneos distintos.\n"
    
    #Definimos el tamaño de la matriz con los APs
    matriz_salida=np.ones((numero_scaneos,len(identificadores)))*(inv_value)
    #Definimos el tamaño de la matriz de etiquetas
    matriz_etiquetas=np.zeros((numero_scaneos,2))
    #Definimos el tamaño de la matriz de tiempos. Como son strings hay que definir el tamaño de cada item
    matriz_time=np.chararray((numero_scaneos,1),itemsize = 27, unicode = True)
    
    set_datos = 0
    offset = 0
    muestra_anterior = 0
    
    #Colocamos los datos de forma ordenada según aparezcan en la lista de identificadores
    for ciclo, element in enumerate(matriz_scan):
        #Nos aseguramos que la dirección MAC este en la lista, si no algo ha fallado
        assert element[2] in identificadores.tolist(), "La dirección MAC "+str(element[2])+" del elemento "+str(ciclo)+" no se había listado."
        
        if((int(element[0])!=int(muestra_anterior)) & (int(muestra_anterior) ==secuencias[set_datos])):
            offset = offset + secuencias[set_datos] +1
            set_datos=set_datos+1
            
        
        fila = offset + int(element[0])
        columna = np.where(identificadores == element[2])
        
        matriz_salida[fila,int(columna[0])] = element[3]
        matriz_etiquetas[fila] = [float(s) for s in re.findall(r'-?\d+\.?\d*', str(element[5]))]

        #Guardamos las marcas de tiempo
        matriz_time[fila] = element[4]
        
        muestra_anterior = element[0]
    
    listado = identificadores
        
    #Si está indicado que se añadan las etiquetas
    if(etiquetas_juntas == True):
        matriz_salida = np.concatenate((matriz_salida, matriz_etiquetas), axis=1)
        matriz_etiquetas = None
        listado = np.concatenate((listado, ["Latitud","Longitud"]), axis=0)
    
    #Si esta indicado que se añadan las marcas temporales
    if(add_time == True):
        print("He entrado en add time.")
        matriz_salida = np.concatenate((matriz_salida, matriz_time), axis=1)
        matriz_time = None
        listado = np.concatenate((listado, ["Time stamp"]), axis=0)
    
    return (matriz_salida, matriz_etiquetas, matriz_time, listado)

def Organizador_general(matriz_scan, secuencias, identificadores=None, borrar_nuevos=False, etiquetas_juntas=False, add_time=False):
    #En la primera columna de la matriz se almacena el número de escaneo, así que para saber cuantos escaneos hay leemos el valor de la primera columna de la última fila
    numero_scaneos=sum(secuencias)+len(secuencias) #Como empiezan en 0 sumamos 1 por cada secuencia
    print("Localizados "+str(numero_scaneos)+" escaneos distintos")
    globals()["str_info"]=globals()["str_info"] + "Localizados "+str(numero_scaneos)+" escaneos distintos.\n"
    
    cuenta=0
    set_datos = 0
    offset = 0
    muestra_anterior = 0
    
    #Si se ha introducido una lista de etiquetas debemos seguirla
    if identificadores is not None:
        lista_Aps = identificadores
        print("La lista con los APs original era de tamaño "+str(len(lista_Aps)))
        
        if(borrar_nuevos == False):
            #Comprobamos si la direccion MAC pertenece al listado, y de no ser así la añadimos al final
            for element in matriz_scan:
                if(element[2] not in lista_Aps.tolist()):
                    lista_Aps = np.append(lista_Aps, element[2])
                    cuenta=cuenta+1
                    #print("La señal: "+str(element)+" no pertenece al listado")
            print("Tras revisar los datos de entrada se han encontrado "+str(cuenta)+" APs nuevos, por lo que finalmente se han listado "+str(len(lista_Aps))+" Aps.")
            globals()["str_info"]=globals()["str_info"] + "[Importante]: La lista con los APs original era de tamaño "+str(len(identificadores))+ ". Tras revisar los datos de entrada se han encontrado "+str(cuenta)+" APs nuevos, por lo que finalmente se han listado "+str(len(lista_Aps))+" Aps.\n"

        else:
            print("[Importante]: Seleccionada la opción para omitir los APs que no aparezcan en la lista original (ya sea la introducida manualmente o la generada en el entrenamiento)")
            globals()["str_info"]=globals()["str_info"] + "[Importante]: Seleccionada la opción para omitir los APs que no aparezcan en la lista original (ya sea la introducida manualmente o la generada en el entrenamiento)"
            
    
    #Si no se introduce una lista para organizar los AP creamos una propia
    else:
        #Creamos la lista de los diferentes APs
        Aps_unicos = np.zeros(matriz_scan.shape[0])
        Aps_unicos = matriz_scan[:,2]
        
        if(ordenar_listas==False):
            #Si no queremos ordenar la lista mostramos las direcciones MAC conforme vayan apareciendo
            print("Como ha seleccionado la opción para no ordenar la lista, se esta procesando usando un bucle for, por lo que este paso puede tomar un poco de tiempo.")
            lista_Aps = []            
            for element in Aps_unicos:
                if element not in lista_Aps: lista_Aps.append(element)
            lista_Aps=np.array(lista_Aps)
            
        else:
            lista_Aps = np.unique(Aps_unicos)
        
        print("No se ha introducido ninguna lista, por lo que se procede a organizar los APs conforme aparecen en los csv.\nEn total se han encontrado "+ str(len(Aps_unicos))+" direcciones MAC diferentes. Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) )
        globals()["str_info"]=globals()["str_info"] + "No se ha introducido ninguna lista, por lo que se procede a organizar los APs conforme aparecen en los csv.\nEn total se han encontrado "+ str(len(Aps_unicos))+" direcciones MAC diferentes. Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10])+"\n"
        
    #Definimos el tamaño de la matriz con los APs
    matriz_salida=np.ones((numero_scaneos,len(lista_Aps)))*(inv_value)
    #Definimos el tamaño de la matriz de etiquetas
    matriz_etiquetas=np.zeros((numero_scaneos,2))
    #Definimos el tamaño de la matriz de tiempos
    matriz_time=np.chararray((numero_scaneos,1),itemsize = 27, unicode = True)
        
    #Colocamos los datos de forma ordenada según aparezcan en la lista de identificadores
    for ciclo, element in enumerate(matriz_scan):
        
        #Si no borras los APs fuera de la lista los pones al final según vayan apareciendo
        if(borrar_nuevos == False):
            #Nos aseguramos que la dirección MAC este en la lista, si no algo ha fallado
            assert element[2] in lista_Aps.tolist(), "La dirección MAC "+str(element[2])+" del elemento "+str(ciclo)+" no se había listado."

            if((int(element[0])!=int(muestra_anterior)) & (int(muestra_anterior) ==secuencias[set_datos])):
                offset = offset + secuencias[set_datos] +1
                set_datos=set_datos+1

            fila = offset + int(element[0])
            #print(fila, offset, int(element[0]),secuencias[set_datos])
            columna = np.where(lista_Aps == element[2])
            #print(columna[0], element[2])
            matriz_salida[fila,int(columna[0])] = element[3]

        #Si quieres borrar los datos cuando aparezca un AP que no está en la lista no lo añades 
        else:
            if((int(element[0])!=int(muestra_anterior)) & (int(muestra_anterior) ==secuencias[set_datos])):
                offset = offset + secuencias[set_datos] +1
                set_datos=set_datos+1

            fila = offset + int(element[0])
            #print(fila, offset, int(element[0]),secuencias[set_datos])
            columna = np.where(lista_Aps == element[2])
            #Si no ha encontrado el AP en la lista no lo añadimos
            if (len(columna[0]) != 0):
                #print(columna[0], element[2])
                matriz_salida[fila,int(columna[0])] = element[3]
        
        muestra_anterior = element[0]

        #Guardamos las marcas de tiempo
        matriz_time[int(element[0])] = element[4]
            
        #Si hay etiquetas
        if(len(element) >= 5):
            if(element[5][2]=="."):
                matriz_etiquetas[fila] = [float(s) for s in re.findall(r'-?\d+\.?\d*', str(element[5]))]
                hay_etiquetas = True

    #Devolvemos el listado
    listado = lista_Aps
    
    #Si está indicado que se añadan las etiquetas
    if(etiquetas_juntas == True & ("hay_etiquetas" in locals())):
        matriz_salida = np.concatenate((matriz_salida, matriz_etiquetas), axis=1)
        matriz_etiquetas = None
        listado = np.concatenate((listado, ["Latitud","Longitud"]), axis=0)
    
    #Si está indicado que se añadan las marcas de tiempo
    if(add_time == True):
        matriz_salida = np.concatenate((matriz_salida, matriz_time), axis=1)
        matriz_time = None
        listado = np.concatenate((listado, ["Time stamp"]), axis=0)
    
    return (matriz_salida, matriz_etiquetas, matriz_time, listado)

# ### Obtención de las matrices
lista_procesar=[
    "matriz_Train",
    "matriz_Test",
    "matriz_Val"
]

str_info = str_info + "\n\u25BA Obtención de las matrices \u25C4\n"

#Vamos procesando las matrices de una en una
for element in lista_procesar:
    if element in globals():
        print("\033[1m" + str(element[7:])+ "\033[0m")
        str_info = str_info + str(element[7:]) +"\n"
        
        #Si se trata del conjunto de entrenamiento sabemos que siempre tendremos una lista
        if("Train" in element):
            globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["matriz_"+'%s'%element[7:]+"_timestamp"], globals()["listado_"+'%s'%element[7:]] = Organizador_entrenamiento(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], globals()["listado_base_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]], add_time=add_timestamp)
        
        #Si es el conjunto de testeo o validacion puede haber varios escenarios
        else:
            #Si tenemos una lista base le damos prioridad
            if("listado_base_"+ str(element[7:]) in globals()):
                print("Matriz obtenida a partir de una lista base.")
                str_info = str_info + "Matriz obtenida a partir de una lista base.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["matriz_"+'%s'%element[7:]+"_timestamp"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], globals()["listado_base_"+'%s'%element[7:]], borrar_nuevos = globals()["borrar_datos_nuevos_" +'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]], add_time=add_timestamp)
            
            #Si no tenemos lista base pero tenemos datos de entrenamiento lo lógico será que organizemos los datos siguiendo dicha lista    
            elif("matriz_Train" in globals()):
                print("Matriz obtenida a partir de los datos de entrenamiento. Los AP's específicos de esta parte se encuentran al final")
                str_info = str_info + "Matriz obtenida a partir de los datos de entrenamiento. Los AP's específicos de esta parte se encuentran al final.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["matriz_"+'%s'%element[7:]+"_timestamp"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], listado_base_Train, borrar_nuevos = globals()["borrar_datos_nuevos_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]], add_time=add_timestamp)
            
            #Si no estamos en ninguno de los casos anteriores no indicamos ningún orden
            else:
                print("Matriz obtenida a partir de los datos crudos sin ninguna referencia.")
                str_info = str_info + "Matriz obtenida a partir de los datos crudos sin ninguna referencia.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["matriz_"+'%s'%element[7:]+"_timestamp"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]], add_time=add_timestamp)
        
        print("Resultado de tamaño "+str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[0])+ "x" +str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[1])+".\n Aquí un ejemplo de las primeras 10 filas y columnas:\n"+ str(globals()["matriz_"+'%s'%element[7:]+"_organizada"][:10,:10]))
        str_info = str_info + "Resultado de tamaño "+str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[0])+ "x" +str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[1])+".\n Aquí un ejemplo de las primeras 10 filas y columnas:\n"+ str(globals()["matriz_"+'%s'%element[7:]+"_organizada"][:10,:10]) + "\n"
        
#Recuento del tiempo
tiempo_matriz = time.time()
tiempo_total = tiempo_matriz-tiempo_inicio

segundos=tiempo_total
 
horas=int(segundos/3600)
segundos-=horas*3600
minutos=int(segundos/60)
segundos-=int(minutos*60)
segundos =int(segundos)

print("\n\u23F3%s:%s:%s" % (horas,minutos,segundos))
str_info = str_info + "\n\t\u23F3 En total el procesado de la matriz ha tardado " + str(horas) +":"+str(minutos)+":"+str(segundos)+".\n"

#Verificaión del valor mínimo
if(check_minimun == True):
    # Comprobamos los valores 
    if "matriz_Train_organizada" in globals():
        if (junto_Train==True) & (add_timestamp==True):
            valores = np.unique(matriz_Train_organizada[:,0:-3])
        elif (junto_Train==True) & (add_timestamp==False):
            valores = np.unique(matriz_Train_organizada[:,0:-2])
        elif (junto_Train==False) & (add_timestamp==True):
            valores = np.unique(matriz_Train_organizada[:,0:-1])
        else:
            valores = np.unique(matriz_Train_organizada)

        maximo = np.amax(valores)
        minimo = np.amin(valores)
        print(maximo,minimo)
        print("Los valores que han aparecido en la matriz de entrenamiento son" + str(valores))
        str_info = str_info + "Los valores que han aparecido en la matriz de entrenamiento son" + str(valores)+"\n"

        if(minimo < inv_value):
            valores_menores = [valor for valor in valores if valor < inv_value]
            val_y_frec = [str("Valor " +str(valor)+" aparece "+str(np.count_nonzero(matriz_Train_organizada == valor))+" veces.") for valor in valores_menores]
            print("\t\u2620Cuidado, has asignado un valor a los puntos de acceso no visbles que es menor que uno (o más) de los valores encontrados.\nEsta es la lista de valores inferiores al asignado y la frecuencia con la que han aparecido cada uno de ellos: "+str(val_y_frec))
            str_info = str_info + "\t\u2620Cuidado, has asignado un valor a los puntos de acceso no visbles que es menor que uno (o más) de los valores encontrados.\nEsta es la lista de valores inferiores al asignado y la frecuencia con la que han aparecido cada uno de ellos: "+str(val_y_frec) +"\n"
        else:
            print("Ningún valor es inferior al asignado.")
            str_info = str_info + "Ningún valor es inferior al asignado." + "\n"
            
# ## Escritura de los datos procesados(*)
if(os.path.exists(date_path)!=True):
    os.mkdir(date_path)
    
#Dentro de dicha carpeta creamos otra con la hora en la cual guardaremos los resultados
os.mkdir(hour_path)

#Creacion de los indices de las filas
lista_indices=[
    "index_Train",
    "index_Test",
    "index_Val"
]

for indice in lista_indices:
    
    if("secuencias_"+indice[6:] in globals()):
        print("secuencias_"+indice[6:])
        globals()["index_"+str(indice[6:])]=[]

        for secuencia in globals()["secuencias_"+indice[6:]]:
            globals()["index_"+str(indice[6:])] = globals()["index_"+str(indice[6:])] + list(range(secuencia+1))

#Pasamos cada matriz a csv y las guardamos en la carpeta.
#Pasamos cada matriz a csv y las guardamos en la carpeta.
lista_matrices =[
    "matriz_Train_organizada",
    "matriz_Train_etiquetas",
    "matriz_Train_timestamp",
    "matriz_Test_organizada",
    "matriz_Test_etiquetas",
    "matriz_Test_timestamp",
    "matriz_Val_organizada",
    "matriz_Val_etiquetas",
    "matriz_Val_timestamp",
    "listado_Train",
    "listado_Test",
    "listado_Val",
    "orden_Train",
    "orden_Test",
    "orden_Val"
]

for matriz in lista_matrices:    
    #Comprobamos si la matriz existe
    if (matriz in globals()):
        #Si existe comprobamos si no está vacía
        if(globals()['%s' % matriz] is not None):
            file_path = hour_path + "/" + matriz + ".csv"
            
            if(matriz[:7] == "listado"):
                (pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False, header=False)
            
            elif(matriz[-16:]=="Train_organizada"):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Train, columns= listado_Train)).to_csv(file_path)
            
            elif(("etiquetas" in matriz) or ("timestamp" in matriz)):
                
                if("etiquetas" in matriz):
                    col = ["Latitud", "Longitud"]
                elif("timestamp" in matriz):
                    col = ["Marca de tiempo"]
                    
                if ("Train" in matriz):
                    ind = index_Train
                elif("Test" in matriz):
                    ind = index_Test
                elif("Val" in matriz):
                    ind = index_Val
                else:
                    ind=False
                
                (pd.DataFrame(globals()['%s' % matriz],index = ind, columns = col)).to_csv(file_path)
            
            elif("Test_organizada" in matriz):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Test, columns= listado_Test)).to_csv(file_path)
            
            elif("Val_organizada" in matriz):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Val, columns= listado_Val)).to_csv(file_path)
            
            elif("orden" in matriz):
                (pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False, header=False)
                
            else:
                (pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False)

            print(str(matriz) + " guardada en " +file_path)

#Recuento del tiempo
tiempo_fin = time.time()
tiempo_total = tiempo_fin-tiempo_inicio

segundos=tiempo_total
 
horas=int(segundos/3600)
segundos-=horas*3600
minutos=int(segundos/60)
segundos-=int(minutos*60)
segundos =int(segundos)

print("\u23F3%s:%s:%s" % (horas,minutos,segundos))
str_info = str_info + "\n\u23F3 En total el programa ha tardado " + str(horas) +":"+str(minutos)+":"+str(segundos)+".\n" 

#Escribimos el .txt
informacion = open(hour_path + "/informacion.txt", "w")
informacion.write(str_info)
informacion.close()

#Acabamos el programa
print("\033[1mPrograma finalizado con éxito\033[0m")
