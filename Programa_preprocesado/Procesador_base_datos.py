#!/usr/bin/env python
# coding: utf-8

# # Script para gestionar el procesadoo de la base de datos

# El objetivo es crear un script capaz de gestionar los archivos csv que se coloquen en una carpeta

# ## Librerías

# In[1]:


#Para gestionar el directorio
import os
import time

#Para filtrar los datos
import pandas as pd
import re
import numpy as np


# ## Creación del espacio de trabajo
# Esta parte del código se encargará de crear las diferentes carpetas en las que se almacenarán los datos procesados. Para ello lo primero que haremos en verificar si ya existe la configuración adecuada, y de no ser así se creará, indicando al usuario como ha de proceder.
# La idea es que el arbol de trabajo sea el siguiente:
# 
#     |->Database
#         |->Raw_data
#             |->Unlisted_data
#             |->Train
#             |->Test
#             |->Val
#         |->Processed_data
#             |->Dia
#                 |->Hora
#             
# En la carpeta "Raw_data" es donde irían los .csv que se van a procesar. Dentro de la misma hay varias opciones a la hora de procesar los datos:
# * Si se añaden csv en las carpetas "Train", "Test" y "Val" esos datos se usarán para dicho proceso.
# * Si se añaden listas que contengan "listado" en el nombre a alguna de las carpetas los datos de ese conjunto se procesaran siguiendo dicho listado.
# 
# Finalmente los datos procesados se pueden recoger en la carpeta "Processed_data". Para evitar que se sobreescriban los datos se crea una carpeta cada vez que se lanza el programa, en la cual se indica el día (carpeta general) y la hora (subcarpeta en la que se guardan los datos procesados).
# 
# En la carpeta de datos procesados siempre encontraras uno o varios archivos .csv (dependiendo de cuantos conjuntos vayas a crear y de si quieres las etiquetes juntas o separadas), junto con el listado de los AP's únicos que se ha usado para procesarlos y un .txt con información diversa del proceso.

# In[2]:


#Función para crear las carpetas a partir de una lista de direcciones
def Crea_directorios(lista):
  for direccion in lista:
    os.mkdir(direccion)


# In[3]:


#Definimos todas las direcciones necesarias.
current_path = os.getcwd()
external_path = current_path + "/Database"

raw_path = external_path + "/Raw_data"
raw_unlisted_path = raw_path + "/Unlisted_data"
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

lista_direcciones=[external_path,raw_path,raw_unlisted_path,raw_train_path,raw_test_path,raw_val_path,processed_path]

#Primero comprobamos si existe la carpeta adecuada. 
if(os.path.exists(external_path)):
    print("Encontrada la carpeta 'Database'. Procedemos a verificar que es la adecuada.")
    if(os.path.exists(raw_path) & os.path.exists(processed_path)):
        if(os.path.exists(raw_unlisted_path) & os.path.exists(raw_train_path) & os.path.exists(raw_test_path) & os.path.exists(raw_val_path)):
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
print("\033[1m[importante]\033[0m: Por favor, no introduzca nada en la carpeta 'Unlisted_data'.")
#print("Pd: Puede hacer ambas cosas a la vez.")

#Creamos una espera por si no se han metido los datos
input("Cuando tengas todo listo pulsa el botón \033[1m'Enter'\033[0m y procederemos con el procesado de los datos.")

# Empezamos a contar para saber cuanto tardamos en ejecutar el programa
tiempo_inicio = time.time()

# ## Obtención de los datos
# En esta parte del código  trabajaremos en los archivos .csv que se encuentren en la carpeta "Raw_data". La idea es que el código lea todos los archivos que encuentre y los procese, independientemente de la cantidad, por lo que el usuario es libre de meter cuantos archivos quiera.

# ### Carga de datos

# Primero comprobamos que haya algún dato a procesar en alguna de las carpetas, y de no ser así avisamos al usuario para que los meta. 
# Dejamos listadas las ubicaciones para facilitar su procesado.

# In[4]:


Lista_procesar=[]

#Unlisted
if(len(os.listdir(raw_unlisted_path))==0):
    print("La carpeta '\033[1mUnlisted_data\033[0m' esta vacia.")
else:
    print("Se han encontrado los siguientes archivos en la carpeta '\033[1mUnlisted_data\033[0m':")
    for file in os.listdir(raw_unlisted_path):
        print(file)
    print("Ya ha sido listado." if len(os.listdir(raw_unlisted_path))==1 else "Ya han sido listados.")    
    Lista_procesar.append("Unlisted_data")

#Train
if(len(os.listdir(raw_train_path))==0):
    print("La carpeta '\033[1mTrain\033[0m' esta vacia.")
else:
    print("Se han encontrado los siguientes archivos en la carpeta '\033[1mTrain\033[0m':")
    
    str_info = str_info +"Se han extraido datos de los siguientes archivos localizados en la carpeta 'Train':\n"   
    
    for file in os.listdir(raw_train_path):
        print("\t \u23FA"+str(file))
        str_info = str_info + "\t \u23FA"+ str(file) +"\n"
    
    print("Ya ha sido listado." if len(os.listdir(raw_train_path))==1 else "Ya han sido listados.")    
    Lista_procesar.append("Train")
    
#Test
if(len(os.listdir(raw_test_path))==0):
    print("La carpeta '\033[1mTest\033[0m' esta vacia.")
else:
    print("Se han encontrado los siguientes archivos en la carpeta '\033[1mTest\033[0m':")
    
    str_info = str_info +"Se han extraido datos de los siguientes archivos localizados en la carpeta 'Test':\n"
    
    for file in os.listdir(raw_test_path):
        print("\t \u23FA"+str(file))
        str_info = str_info + "\t \u23FA"+ str(file) +"\n"
        
    print("Ya ha sido listado." if len(os.listdir(raw_test_path))==1 else "Ya han sido listados.")    
    Lista_procesar.append("Test")

#Val    
if(len(os.listdir(raw_val_path))==0):
    print("La carpeta '\033[1mVal\033[0m' esta vacia.")    
else:
    print("Se han encontrado los siguientes archivos en la carpeta '\033[1mVal\033[0m':")
    
    str_info = str_info +"Se han extraido datos de los siguientes archivos localizados en la carpeta 'Val':\n"
    
    
    for file in os.listdir(raw_val_path):
        print("\t \u23FA"+str(file))
        str_info = str_info + "\t \u23FA"+ str(file) +"\n"
        
    print("Ya ha sido listado." if len(os.listdir(raw_val_path))==1 else "Ya han sido listados.")    
    Lista_procesar.append("Val")

#Verificamos que al menos una de las carpetas este vacia, si no avisamos al usuario para que meta los datos
assert len(Lista_procesar) != 0, "No se han encontrado datos en ninguna carpeta. Por favor introduzca algún csv."
print("Registro finalizado con éxito. Procedemos a extraer los datos de "+ str(Lista_procesar))


# In[5]:


#Borramos las variables para que no den problemas en caso de que no existan.
if("direcciones_Train" in globals()):
  del direcciones_Train
if("direcciones_Test" in globals()):
  del direcciones_Test
if("direcciones_Val" in globals()):
  del direcciones_Val
if("direcciones_Unlisted_data" in globals()):
  del direcciones_Unlisted_data

#Si no hay nada en "unlisted_data" podemos extraer los datos libremente
if ("Unlisted_data" not in Lista_procesar):
    print("No hay datos sin listar.")
    for elemento in Lista_procesar:
        #globals()['direcciones_%s' % elemento] = [files for files in os.listdir(raw_path + "/" + elemento)]
        path = raw_path + "/" + elemento
        globals()['direcciones_%s' % elemento] =  [path +"/" + files for files in os.listdir(path)]
        
        #Ordenamos los elementos en orden alfabetico
        globals()['direcciones_%s' % elemento] = np.unique(globals()['direcciones_%s' % elemento]).tolist()
        print("Los ficheros del conjunto \033[1m"+ str(elemento) +"\033[0m se han ordenado según su nombre para ser procesados:\n" + str(globals()['direcciones_%s' % elemento]))
        str_info = str_info + "Los ficheros del conjunto "+ str(elemento) +" se han ordenado según su nombre para ser procesados:\n" + str(globals()['direcciones_%s' % elemento])

else:
    print("Si que esta")


# ### Función para sacar las matrices
# 
# Una vez tenemos listadas las direcciones de todos los archivos que vamos a procesar, creamos una función que tendrá como entrada ese listado y como salida una matriz con todos datos.
# La variable "secuencia" cuenta con las muestras que tiene cada fichero csv, de forma que acaba siendo una lista donde se guardan todas las secuencias que se han procesado.
# También en el caso de que exista un fichero "listado" en alguna de las carpetas lo procesará para que se puedan ordenar los datos conforme allí aparezcan.

# In[6]:


def Saca_matrices(direcciones):
    #Almacenaremos los datos en una lista de listas de tamaño variable en función de la cantidad de ficheros que haya
    datos_totales=[]
    secuencias=[]
    listado = None
    
    #Para cargar los datos usamos pd.read_csv(), el cual nos carga los datos en formato Dataframe, pero nosotros lo convertiremos a lista para poder trabajar con ello
    for direccion in direcciones:
        #Comprobamos que no sea un archivo de listado
        if("listado" in direccion):
            listado = pd.read_csv(direccion, header = None).to_numpy()[1:]
            listado = np.array([item for sublist in listado for item in sublist])
            print("[Importante]: Se ha encontrado una lista base")
            globals()["str_info"]=globals()["str_info"] + "[Importante]: Se ha encontrado una lista base\n"
        else:
           datos_totales.append((pd.read_csv(direccion, header = None)).to_numpy().tolist())
    
    #Mostramos la cantidad de datos que se han leido para asegurarnos más tarde de que no se pierda ninguno
    print("En total se han descargado "+ str(len(datos_totales)) +" ficheros, los cuales tienen las siguientes dimensiones:")
    globals()["str_info"]=globals()["str_info"] + "En total se han descargado "+ str(len(datos_totales)) +" ficheros, los cuales tienen las siguientes dimensiones:\n"
    
    cuenta_datos = 0
    for i in range(len(datos_totales)):
        print("El archivo '"+ str(direcciones[i]) +" contenía "+ str(len(datos_totales[i])) +" datos.")
        print("En total representaban "+str(datos_totales[i][-1][0])+" secuencias.")
        globals()["str_info"]=globals()["str_info"] + "\t\u23FA" + "El archivo '"+ str(direcciones[i]) +" contenía "+ str(len(datos_totales[i])) +" datos, los cuales en total representaban "+str(datos_totales[i][-1][0] +1)+" secuencias.\n"
        cuenta_datos = cuenta_datos + len(datos_totales[i])
        secuencias.append(datos_totales[i][-1][0])
    print("Por lo que el total de datos a procesar tiene que ser de "+str(cuenta_datos))
    
    #Una vez cargados los datos los pasaremos de una lista de listas a una sola lista
    flat_list = [item for sublist in datos_totales for item in sublist]
    print("Al realizar el 'aplanamiento' nos quedamos con un total de "+ str(len(flat_list)))
    assert len(flat_list) == cuenta_datos, "Ha surgido un error al aplanar los datos. Originalmente había "+ str(cuenta_datos) +", pero tras aplanar nos hemos quedado con "+ str(len(flat_list)) +".Por favor, revisa el código"
    
    #Escribimos más informacion
    globals()["str_info"]=globals()["str_info"] + "El total de datos a procesar dentro de este conjunto ha de ser de "+str(cuenta_datos)+ ".\n"
    
    #Finalmente convertimos dicha lista a formato matriz para poder trabajar con ella de manera cómoda
    matriz = np.array(flat_list)
    
    return matriz, secuencias, listado


# Y pasamos por la función todas las listas que hayamos creado anteriormente

# In[7]:


#Creamos las listas de entrenamiento, testeo y validación
if("direcciones_Train" in globals()):
    print('\033[1m'+'Set de entrenamiento'+'\033[0m')
    str_info = str_info + "Set de entrenamiento\n"
    matriz_Train, secuencias_Train, listado_base_Train = Saca_matrices(direcciones_Train)
    print("Se ha creado la variable matriz_Train")
else:
    if("matriz_Train" in globals()): del matriz_Train
    if("secuencias_Train" in globals()): del secuencias_Train
    if("listado_base_Train" in globals()): del listado_base_Train

if("direcciones_Test" in globals()):
    print('\033[1m'+'Set de testeo'+'\033[0m')
    str_info = str_info + "Set de testeo\n"
    matriz_Test, secuencias_Test, listado_base_Test = Saca_matrices(direcciones_Test)
    print("Se ha creado la variable matriz_Test")
else:
    if("matriz_Test" in globals()): del matriz_Test
    if("secuencias_Test" in globals()): del secuencias_Test
    if("listado_base_Test" in globals()): del listado_base_Test

if("direcciones_Val" in globals()):
    print('\033[1m'+'Set de validación'+'\033[0m')
    str_info = str_info + "Set de validación\n"
    matriz_Val, secuencias_Val, listado_base_Val = Saca_matrices(direcciones_Val)
    print("Se ha creado la variable matriz_Val")
else:
    if("matriz_Val" in globals()): del matriz_Val
    if("secuencias_Val" in globals()): del secuencias_Val
    if("listado_base_Val" in globals()): del listado_base_Val
        


# ## Procesado de los datos
# 
# Esta parte del código se encargará de procesar las matrices calculadas anteriormente para darlas el formato adecuado antes de exportarlas.

# ### Obtención de las listas de AP's
# 
# Lo primero será comprobar la existencia de alguna lista a la que aferrarse. En el caso de que exista los datos se acomodarán a ella, de lo contrario habrá distintas maneras de proceder.
# 
# Para el caso del entrenamiento, si no hay una lista preestablicida (que es lo esperable) habrá que localizar los diferentes puntos de acceso que aparecen en todos los datos dentro de un conjunto, los cuales pueden no conincidir con los de otros conjuntos (por ejemplo los APs vistos en el entrenamiento pueden ser distintos de los vistos en el testeo).
# Los APs vistos en el entrenamiento marcaran el orden de la matriz, mientras que los de testeo y validación se tendran que ajustar a dicho orden.

# In[8]:


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
        Aps_unicos = np.unique(matriz_Aps)
        print("Entre los datos de entrenamiento se han encontrado un total de "+ str(len(Aps_unicos))+" direcciones MAC diferentes. \nAquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) )
        listado_base_Train = Aps_unicos
        
        str_info = str_info + "Hemos procesado los datos de entrenamiento. En total hemos detectado " +str(len(Aps_unicos))+" direcciones MAC únicas." + "Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) + "\n"



# ### Funciónes para ordenar los datos
# Las siguientes funciones sirven para organizar los datos y crear las matrices finales con las que trabajaremos.

# En el caso de la matriz de entrenamiento esta recibe como parámetros:
# * Identificadores: Una array con las direcciones MAC únicas filtradas anteriormente
# * Matriz_scan: La matriz en la que aparecen los datos leidos de los csv creada anteriormente
# * Etiquetas_juntas (opcional): En caso de que este parámetro sea verdadero las etiquetas se incluirán en la matriz final, de lo contrario se crearán dos matrices separadas.

# In[9]:


def Organizador_entrenamiento(matriz_scan, secuencias, identificadores, etiquetas_juntas=False):
    #En la primera columna de la matriz se almacena el número de escaneo, así que para saber cuantos escaneos hay leemos el valor de la primera columna de la última fila
    numero_scaneos=sum(secuencias)+len(secuencias) #Como empiezan en 0 sumamos 1 por cada secuencia
    print("Localizados "+str(numero_scaneos)+" escaneos distintos")
    globals()["str_info"]=globals()["str_info"] + "Localizados "+str(numero_scaneos)+" escaneos distintos.\n"
    
    #Definimos el tamaño de la matriz con los APs
    matriz_salida=np.ones((numero_scaneos,len(identificadores)))*(-200)
    #Definimos el tamaño de la matriz de etiquetas
    matriz_etiquetas=np.zeros((numero_scaneos,2))
    
    set_datos = 0
    offset = 0
    muestra_anterior = 0
    
    #Colocamos los datos de forma ordenada según aparezcan en la lista de identificadores
    for ciclo, element in enumerate(matriz_scan):
        #Nos aseguramos que la dirección MAC este en la lista, si no algo ha fallado
        assert element[2] in identificadores.tolist(), "La dirección MAC "+str(element[2])+" del elemento "+str(ciclo)+" no se había listado."
        
        if((int(element[0])!=int(muestra_anterior)) & (int(muestra_anterior) ==secuencias[set_datos])):
            offset = secuencias[set_datos] +1
            set_datos=set_datos+1
            
        
        fila = offset + int(element[0])
        #print(fila, offset, int(element[0]),secuencias[set_datos])
        columna = np.where(identificadores == element[2])
        
        matriz_salida[fila,int(columna[0])] = element[3]
        matriz_etiquetas[fila] = [float(s) for s in re.findall(r'-?\d+\.?\d*', str(element[5]))]
        
        muestra_anterior = element[0]
        #print("Fila: "+str(fila)+" columna: "+str(columna))
    
    listado = identificadores
    #Si está indicado que se añadan las etiquetas
    if(etiquetas_juntas == True):
        matriz_salida = np.concatenate((matriz_salida, matriz_etiquetas), axis=1)
        matriz_etiquetas = None
        listado = np.concatenate((listado, ["Latitud","Longitud"]), axis=0)
    
    return (matriz_salida, matriz_etiquetas, listado)


# En el caso del testeo y validación existen varias posibilidades:
# * En caso de que se le introduzca una lista de APs (por ejemplo la del entrenamiento) los datos se acomodarán a la misma, dejando a elección del usuario si borrar los APs que no aparezcan en la lista o si añadirlos al final.
# * Si no se introduce una lista base se procesará la misma y e acomodarán los datos.
# En lo que respecta a las etiquetas lo gestionamos al igual que en el entrenamiento

# In[10]:


def Organizador_general(matriz_scan, secuencias, identificadores=None,  etiquetas_juntas=False):
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
        
        #Comprobamos si la direccion MAC pertenece al listado, y de no ser así la añadimos al final
        for element in matriz_scan:
            if(element[2] not in lista_Aps.tolist()):
                lista_Aps = np.append(lista_Aps, element[2])
                cuenta=cuenta+1
                #print("La señal: "+str(element)+" no pertenece al listado")
        print("Tras revisar los datos de entrada se han encontrado "+str(cuenta)+" APs nuevos, por lo que finalmente se han listado "+str(len(lista_Aps))+" Aps.")
        globals()["str_info"]=globals()["str_info"] + "[Importante]: La lista con los APs original era de tamaño "+str(len(identificadores))+ ". Tras revisar los datos de entrada se han encontrado "+str(cuenta)+" APs nuevos, por lo que finalmente se han listado "+str(len(lista_Aps))+" Aps.\n"
        
        #Definimos el tamaño de la matriz con los APs
        matriz_salida=np.ones((numero_scaneos,len(lista_Aps)))*(-200)
        #Si hay etiquetas definimos el tamaño de la matriz de etiquetas
        matriz_etiquetas=np.zeros((numero_scaneos,2))

    #Si no se introduce una lista para organizar los AP creamos una propia
    else:
        #Creamos la lista de los diferentes APs
        Aps_unicos = np.zeros(matriz_scan.shape[0])
        Aps_unicos = matriz_scan[:,2]
        lista_Aps = np.unique(Aps_unicos)
        print("No se ha introducido ninguna lista, por lo que se procede a organizar los APs conforme aparecen en los csv.\nEn total se han encontrado "+ str(len(Aps_unicos))+" direcciones MAC diferentes. Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10]) )
        globals()["str_info"]=globals()["str_info"] + "No se ha introducido ninguna lista, por lo que se procede a organizar los APs conforme aparecen en los csv.\nEn total se han encontrado "+ str(len(Aps_unicos))+" direcciones MAC diferentes. Aquí te muestro las 10 primeras:\n"+ str(Aps_unicos[0:10])+"\n"
        
        #Definimos el tamaño de la matriz con los APs
        matriz_salida=np.ones((numero_scaneos,len(lista_Aps)))*(-200)
        #Definimos el tamaño de la matriz de etiquetas
        matriz_etiquetas=np.zeros((numero_scaneos,2))
        
    #Colocamos los datos de forma ordenada según aparezcan en la lista de identificadores
    for ciclo, element in enumerate(matriz_scan):
        #Nos aseguramos que la dirección MAC este en la lista, si no algo ha fallado
        assert element[2] in lista_Aps.tolist(), "La dirección MAC "+str(element[2])+" del elemento "+str(ciclo)+" no se había listado."

        if((int(element[0])!=int(muestra_anterior)) & (int(muestra_anterior) ==secuencias[set_datos])):
            offset = secuencias[set_datos] +1
            set_datos=set_datos+1

        fila = offset + int(element[0])
        #print(fila, offset, int(element[0]),secuencias[set_datos])
        columna = np.where(lista_Aps == element[2])
        #print(columna[0], element[2])
        matriz_salida[fila,int(columna[0])] = element[3]

        #Si hay etiquetas
        if(len(element) >= 5):
            if(element[5][2]=="."):
                matriz_etiquetas[int(element[0])] = [float(s) for s in re.findall(r'-?\d+\.?\d*', str(element[5]))]
                hay_etiquetas = True       

    #Si está indicado que se añadan las etiquetas
    if(etiquetas_juntas == True & ("hay_etiquetas" in locals())):
        matriz_salida = np.concatenate((matriz_salida, matriz_etiquetas), axis=1)
        matriz_etiquetas = None

    #Devolvemos el listado
    listado = lista_Aps
    
    return (matriz_salida, matriz_etiquetas, listado)


# ### Obtención de las matrices

# In[11]:


lista_procesar=[
    "matriz_Train",
    "matriz_Test",
    "matriz_Val"
]

#Definimos si queremos las etiquetas en la misma matriz que los datos o por separado
junto_Train = False
junto_Test = False
junto_Val = False

#Vamos procesando las matrices de una en una
for element in lista_procesar:
    if element in globals():
        print("\033[1m" + str(element[7:])+ "\033[0m")
        str_info = str_info + str(element[7:]) +"\n"
        
        #Si se trata del conjunto de entrenamiento sabemos que siempre tendremos una lista
        if("Train" in element):
            globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["listado_"+'%s'%element[7:]] = Organizador_entrenamiento(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], globals()["listado_base_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]])
        
        #Si es el conjunto de testeo o validacion puede haber varios escenarios
        else:
            #Si tenemos una lista base le damos prioridad
            if("listado_base_"+ str(element[7:]) in globals()):
                print("Matriz obtenida a partir de una lista base.")
                str_info = str_info + "Matriz obtenida a partir de una lista base.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], globals()["listado_base_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]])
            
            #Si no tenemos lista base pero tenemos datos de entrenamiento lo lógico será que organizemos los datos siguiendo dicha lista    
            elif("matriz_Train" in globals()):
                print("Matriz obtenida a partir de los datos de entrenamiento. Los AP's específicos de esta parte se encuentran al final")
                str_info = str_info + "Matriz obtenida a partir de los datos de entrenamiento. Los AP's específicos de esta parte se encuentran al final.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], listado_base_Train, etiquetas_juntas = globals()["junto_"+'%s'%element[7:]])
            
            #Si no estamos en ninguno de los casos anteriores no indicamos ningún orden
            else:
                print("Matriz obtenida a partir de los datos crudos sin ninguna referencia.")
                str_info = str_info + "Matriz obtenida a partir de los datos crudos sin ninguna referencia.\n"
                globals()["matriz_"+'%s'%element[7:]+"_organizada"], globals()["matriz_"+'%s'%element[7:]+"_etiquetas"], globals()["listado_"+'%s'%element[7:]] = Organizador_general(globals()['%s'%element], globals()["secuencias_"+'%s'%element[7:]], etiquetas_juntas = globals()["junto_"+'%s'%element[7:]])
        
        print("Resultado de tamaño "+str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[0])+ "x" +str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[1])+".\n Aquí un ejemplo de las primeras 10 filas y columnas:\n"+ str(globals()["matriz_"+'%s'%element[7:]+"_organizada"][:10,:10]))
        str_info = str_info + "Resultado de tamaño "+str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[0])+ "x" +str(globals()["matriz_"+'%s'%element[7:]+"_organizada"].shape[1])+".\n Aquí un ejemplo de las primeras 10 filas y columnas:\n"+ str(globals()["matriz_"+'%s'%element[7:]+"_organizada"][:10,:10]) + "\n"
        


# ## Escritura de los datos procesados
# 
# Finalmente, una vez todos los datos han sido procesados los volvemos a meter a un archivo .csv que localizaremos en la carpeta "Processed_data". Dentro de dicha carpeta creamos otra con la fecha actual, sobre la cual crearemos distintas carpetas con el nombre de la hora en la que se ha guardado información.

# In[12]:


#Finalmente creamos creamos las carpetas donde guardarán los datos
if(os.path.exists(date_path)!=True):
    os.mkdir(date_path)
    
#Dentro de dicha carpeta creamos otra con la hora en la cual guardaremos los resultados
os.mkdir(hour_path)


# In[13]:

#Creacion de los indices de las filas
#print(secuencias_Train)
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

    
#print(len(index_Train), index_Train)
#print(len(index_Test), index_Test)


#Pasamos cada matriz a csv y las guardamos en la carpeta.
lista_matrices =[
    "matriz_Train_organizada",
    "matriz_Train_etiquetas",
    "matriz_Test_organizada",
    "matriz_Test_etiquetas",
    "matriz_Val_organizada",
    "matriz_Val_etiquetas",
    "listado_Train",
    "listado_Test",
    "listado_Val"
]

for matriz in lista_matrices:    
    #Comprobamos si la matriz existe
    if (matriz in globals()):
        #Si existe comprobamos si no está vacía
        if(globals()['%s' % matriz] is not None):
            file_path = hour_path + "/" + matriz + ".csv"
            
            if(matriz[:7] == "listado"):
                #index = globals()["index_"+matriz[8:]]
                #print(index)
                (pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False, header=False)
            
            elif(matriz[-16:]=="Train_organizada"):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Train, columns= listado_Train)).to_csv(file_path)
            
            elif("etiquetas" in matriz):
                if ("Train" in matriz):
                    ind = index_Train
                elif("Test" in matriz):
                    ind = index_Test
                elif("Val" in matriz):
                    ind = index_Val
                else:
                    ind=False
                (pd.DataFrame(globals()['%s' % matriz],index = ind, columns = ["Latitud", "Longitud"])).to_csv(file_path)
     
            elif("Test_organizada" in matriz):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Test, columns= listado_Test)).to_csv(file_path)
            
            elif("Val_organizada" in matriz):
                (pd.DataFrame(globals()['%s' % matriz], index = index_Val, columns= listado_Val)).to_csv(file_path)
            
            else:
                (pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False)

            #(pd.DataFrame(globals()['%s' % matriz])).to_csv(file_path, index=False)
            print(str(matriz) + " guardada en " +file_path)


# In[14]:
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
str_info = str_info + "\u23F3 En total el programa ha tardado " + str(horas) +":"+str(minutos)+":"+str(segundos)+".\n" 


#Escribimos el .txt
informacion = open(hour_path + "/informacion.txt", "w")
informacion.write(str_info)
informacion.close()

#Acabamos el programa
print("\033[1mPrograma finalizado con éxito\033[0m")
