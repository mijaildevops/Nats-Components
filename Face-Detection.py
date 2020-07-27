# Nats 
import asyncio
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
# Hostname
import socket 
# Json
import json
import os
# Time
from datetime import datetime
# Mkdir
from shutil import rmtree 
from os import makedirs
from os import remove
import shutil
# Base64
import base64
from base64 import b64encode
#Request
import requests
# GUID
import uuid 

#///////////////////////////////////////////
# Generamos Un GUID 
#///////////////////////////////////////////
IdUnico = uuid.uuid4()

#///////////////////////////////////////////
# Get Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('[Face Detection] is Running... Nats Server - Host: ', Hostname)

#///////////////////////////////////////////
# crear carpeta
#///////////////////////////////////////////
try:
    FolderFaceDetection = "C:/File-Nats/Face-Detection"
    FolderSubscriber = "C:/File-Nats/Face-Detection/Subscriber"
    FolderPublisher = "C:/File-Nats/Face-Detection/Publisher"
    makedirs(FolderFaceDetection)
    makedirs(FolderSubscriber)
    makedirs(FolderPublisher)
except FileExistsError:
    print ("      - Backup Folders Exist")

#///////////////////////////////////////////
# Validar o Crear File Setting
#///////////////////////////////////////////
dirFolders = 'C:/File-Nats/Face-Detection/Settings.json'

if os.path.isfile(dirFolders):
    print('The file already exists.')
else:
    Setting = {
        'ServerIP' : 'nats://127.0.0.1:4222',
        'ClientId'   : str(IdUnico)
    }
    print('Configuration file does not exist.')
    with open(dirFolders, 'w') as file:
        json.dump(Setting, file)

#///////////////////////////////////////////
# Get Setting from Settings.json
#///////////////////////////////////////////
with open(dirFolders, 'r') as file:
    data = json.load(file)
    ServerIP = data["ServerIP"]
    ClientId = data["ClientId"]

# funcion recibe el mensaje del Sensor Procesor 
async def FrameProces (Secuencia, Data):

    print(' - Connected to channel [VSBLTY-DATA-TEMP] as subscriber ')
    # Secuencia Mensaje
    print ("      - [subscriber] Message received from 'VSBLTY-DATA-TEMP': -", str(Secuencia))

    # Decode UTF-8 bytes mensaje Recibido 
    # to double quotes to make it valid JSON
    JsonNats = Data.decode('utf8').replace("'", '"')

    # mensaje es formatted JSON
    mensaje = json.loads(JsonNats)

    #////////////////////////////////////////////////////////
    # Save Data recibida en formato json (Sensor-Process)
    #////////////////////////////////////////////////////////
    # Fecha para Nombre del archivo Convertir a funcion
    now = datetime.now()
    timestampStr = now.strftime("%Y-%m-%d %H%M%S")

    # Estructura para el Nombre del Archivo
    file_name = str(Secuencia) + " - [Face-Detection] - [Subscriber] - " + str(timestampStr)  + ".json"

    # Ruta del Archivo donde se guardaran los archivos Json
    dir = 'C:/File-Nats/Face-Detection/Subscriber' 

    # Crear Archivo .json con los datos del mensaje Recibido
    with open(os.path.join(dir, file_name), 'w') as file:
        json.dump(mensaje, file)

    Hostname = mensaje["Hostname"]
    Data = mensaje["Data"]
    Temp = mensaje["Temp"]
    FrameTimestamp = mensaje["FrameTimestamp"]

    """ print ("       - ", Hostname)
    print ("       - ", FrameTimestamp)
    print ("       - ", Temp)
    print ("       - ", Data[:10]) """

    #/////////////////////////////////////////////////////////////////////
    # Base 64
    #/////////////////////////////////////////////////////////////////////
    Imagen64Bytes = bytes(str(Data), 'utf8')
    #print (" - ", Imagen64Bytes[:10])
    #print (type(Imagen64Bytes))
    # From 64 to Bites
    ImagenBites = base64.decodestring(Imagen64Bytes) 
    #print ("bites : ",ImagenBites[:6])
    #print (type(ImagenBites))

    #//////////////////////////////////////////////////////////////////////
    # Send request API-VSBLTY
    #/////////////////////////////////////////////////////////////////////
    files = {'file': ImagenBites}  
    #POST to API
    url = "http://openvino-api.vsblty.support:8099/process?raw"
    r=requests.post(url,files=files)

    # the results
    respuesta = str(r.content.decode())
    print('      - [API] Sending Frame with the Detected Person to VSBLTY')

    # build dictionary with data to publish
    data = {}
    data['FrameTimestampId'] = str(FrameTimestamp)
    data['SecuenciaMsg'] = str(Secuencia)
    data['HostnamePublisher'] = str(Hostname)
    data['Data'] = str(Data)
    data['Temp'] = str(Temp)

    # Path
    dir = 'C:/File-Nats/Face-Detection/Publisher'  

    # Estructura para el Nombre del Archivo
    file_name = str(Secuencia) + " - [Face-Detection] - [Publisher] - " + str(timestampStr)  + ".json"

    # Decode UTF-8 bytes mensaje Recibido 

    # mensaje es formatted JSON
    mensaje = json.loads(respuesta)

    # Add result Request Api Vsblty
    data['FaceDetection'] = mensaje

    # Crear Archivo .json con los datos del mensaje Recibido
    with open(os.path.join(dir, file_name), 'w') as file:
        json.dump(data, file)

    return data

#/////////////////////////////////////////////////////////////////
# Funcion error de Conexion
#/////////////////////////////////////////////////////////////////
async def error_cb(e):
    print("Error:", e)

#/////////////////////////////////////////////////////////////////
# Conexion a Nats Server
#/////////////////////////////////////////////////////////////////
async def run(loop, ClientId, ServerIP):

    nc = NATS()
    sc = STAN()

    options = {
        "servers": [ServerIP],
        "io_loop": loop,
        "error_cb": error_cb
    }

    await nc.connect(**options)

    # Start session with NATS Streaming cluster using
    # the established NATS connection.
    await sc.connect("vsblty-cluster", ClientId, nats=nc)
    
    async def cb(msg):

        # Creando task, llamando a la Funcion FrameProces
        task1 = await loop.create_task(FrameProces(msg.seq, msg.data))

        #/////////////////////////////////////////////////////////////////////////////
        # Publicar Mensaje con el resultado en el canal VSBLTY-DATA-FACE
        #/////////////////////////////////////////////////////////////////////////////
        ChannelNats = 'VSBLTY-DATA-FACE'
        # Definir Channel y Mensaje
        await sc.publish(ChannelNats, bytes(str(task1), 'utf8'))
        print ("      - [publisher] -  Sending Message To Channel 'VSBLTY-DATA-FACE': - " + str(msg.seq))
        print ('')

    # Subscribe to get all messages from the beginning.
    await sc.subscribe("VSBLTY-DATA-TEMP", start_at='first', cb=cb)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, ClientId, ServerIP))
    loop.run_forever()