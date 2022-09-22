#!/usr/bin/env python
# coding: utf-8

#Librerias
import os
import pandas as pd
import numpy as np


# ## Definición de las direcciones
#Indique que el conjunto que quiere revisar
Conjunto = "Train" 

#Indique el nombre del fichero en el que se encontraban los datos originales (direccion a partir de la carpeta del conjunto)
Nombre_fichero_original = "Mes2202-28022022/Nexus/t1_Nexus.csv" 

#Indique la fecha y la hora en la que se procesaron los datos
Fecha = "22_9_2022"
Hora = "8:44:44"


#Definición de las direcciones 
current_path = os.getcwd()
path_original_data = current_path + "/Database/Raw_data" + "/"+ Conjunto +"/" + Nombre_fichero_original
path_processed_data = current_path + "/Database/Processed_data" + "/"+ Fecha +"/"+Hora+"/matriz_"+Conjunto +"_organizada.csv"
path_info_data = current_path + "/Database/Processed_data" + "/"+ Fecha +"/"+Hora+"/orden_"+Conjunto +".csv"

#Nos aseguramos de que las direcciones existan
assert os.path.exists(path_original_data), "Dirección " + str(path_original_data) + " de los datos originales errónea."
print("Datos originales encontrados." if os.path.exists(path_original_data) else "Dirección de los datos originales errónea.")

assert os.path.exists(path_processed_data), "Dirección " + str(path_processed_data) + " de los datos procesados errónea."
print("Datos procesados encontrados." if os.path.exists(path_processed_data) else "Dirección de los datos procesados errónea.")

assert os.path.exists(path_info_data), "Información de los datos errónea. revise que la direccion "+str(path_info_data)+" sea correcta."
print("Información de los datos encontrada." if os.path.exists(path_info_data) else "Información de los datos errónea.")


# ## Obtención de las matrices
#Datos originales
datos_originales=(pd.read_csv(path_original_data, on_bad_lines='skip', header = None)).to_numpy().tolist()
print("\u25CF Cinco primeras filas de \033[1mdatos sin procesar\033[0m:\n" + str(datos_originales[:5]))

#Información de los datos
info_data=(pd.read_csv(path_info_data, on_bad_lines='skip', header = None)).to_numpy().tolist()
print("\u25CF Cinco primeras filas de \033[1minformación\033[0m:\n"+str(info_data[:5]))

#Datos procesados
datos_procesados=pd.read_csv(path_processed_data, on_bad_lines='skip')

matriz = datos_procesados.to_numpy()
columnas = (datos_procesados.columns).to_numpy().tolist()
print("\u25CF \033[1mMatriz procesada\033[0m")
print("En total hay " + str(len(columnas)) + " columnas, que representan distintos AP's (y la primer vacía que hace referencia al numero de muestra). Aquí te muestro las 5 primeras:\n"+str(columnas[:5]))
print("El resto de la matriz es de tamaño "+str(matriz.shape[0])+"x"+str(matriz.shape[1])+ ". Aquí un ejemplo de las primeras 5 filas y columnas:\n"+str(matriz[:5,:5]))


# ## Localización de los datos iniciales
#Sacamos las listas con las direcciones y con las secuencias
direcciones = [item[0] for item in info_data]
secuencias = [item[1] for item in info_data]

#Localizamos la fila en la que se encuentran nuestros datos
iden = direcciones.index(path_original_data)

fila_inicio = sum(secuencias[:iden])+(iden)


# ## Comprobamos que los valores coincidan
id_fallo=[]
MAC_fallo=""
muestra_fallo=0
fallos_repeticion=0

for i,element in enumerate(datos_originales):    
    
    #Comprobamos que este la dirección MAC en la lista de columnas
    if(element[2] in columnas):
        
        col = columnas.index(element[2])
        fila=fila_inicio+element[0]
        if((element[0] == muestra_fallo) and (element[2] == MAC_fallo)):
            print("\u2192Fallo por repetición de MAC.")
            fallos_repeticion+=1
        
        if(element[3]!=matriz[fila][col]):
            print("\u25CF \033[1mAlgo ha fallado\033[0m")
            print("Fila: "+str(fila)+"  Columna: "+str(col))
            print("Mac: "+str(element[2])+", número de muestra: "+str(element[0]))
            print("Valor esperado: "+str(element[3])+  ", valor obtenido: "+ str(matriz[fila][col]))
            
            muestra_fallo = element[0]
            MAC_fallo = element[2]
                       
            if(element[2] not in id_fallo):
                id_fallo.append([element[2],i,fila,col])
    
    #Si no lo está sacamos el error
    else:
        print("\u25CF \033[1mFallo al encontrar la columna\033[0m")

                
# ## En caso de fallo
dic ={
    "1" : "A",
    "2" : "B",
    "3" : "C",
    "4" : "D",
    "5" : "E",
    "6" : "F",
    "7" : "G",
    "8" : "H",
    "9" : "I",
    "10" : "J",
    "11" : "K",
    "12" : "L",
    "13" : "M",
    "14" : "N",
    "15" : "O",
    "16" : "P",
    "17" : "Q",
    "18" : "R",
    "19" : "S",
    "20" : "T",
    "21" : "U",
    "22" : "V",
    "23" : "W",
    "24" : "X",
    "25" : "Y",
    "26" : "Z"
}

def Traductor_excel(fila, columna):
    
    base=26
    digitos=[]
    valor=columna+1
    resultado= ""
    
    continua = True
    
    while (continua==True):
        
        digitos.append((valor%base))
        valor = int(valor/base)
        
        if(valor <= base):
            digitos.append(valor)
            continua=False
    
    for digito in reversed(digitos):
        resultado += dic[str(digito)]
    
    resultado += str(fila+2)
    
    return resultado

print("Fallos encontrados: "+str(len(id_fallo))+", de los cuales " +str(fallos_repeticion)+ " han sido por repetición de MAC.")
for fallo in id_fallo:
    print("\u25CF \033[1mRevisar:\033[0m")
    print("\t \u2192 En los datos originales la fila " + str(fallo[1]+1)+" que se ha de corresponder con la MAC "+str(fallo[0]))
    print("\t \u2192 En la matriz procesada la casilla " + str(Traductor_excel(fallo[2], fallo[3])))
    
