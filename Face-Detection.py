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
#Opencv
import cv2


#///////////////////////////////////////////
# Get Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('Runing... Nats Subscriber')

#///////////////////////////////////////
# Request Vsblty
#////////////////////////////////////////
async def ApiRequest():
    #JUST to get the image into memory. Your code will probably already have a file in memory from the Dermalog API. You don't need to write to disk. 
    im = cv2.imread('test.jpg')   
    #Create a object with byte array of file. Only needed if image is in a OpenCV image. If it is just a byte[] file it can be posted directly
    is_success, im_buf_arr = cv2.imencode(".jpg", im)
    byte_im = im_buf_arr.tobytes()

    #Place the file in the files array for the post method
    files = {'file': byte_im}

    #POST to API
    url = "http://openvino-api.vsblty.support:8099/process?raw"
    r=requests.post(url,files=files)
    print (r.status_code)

    #Print the results
    #print(str(r.content.decode()))
    FrameAnalisis = str(r.content.decode())
    #print (FrameAnalisis)
    return FrameAnalisis

async def JsonFrameProcess(seq):
    print ('Json Save')
    print (seq)
    #print (task1)
    x =  '{ "name":"John", "age":30, "city":"New York"}'
    y = json.loads(x)

    dir = 'C:/File-Nats/VSBLTY-DATA-FACE'  
    # Crear Archivo .json con los datos del mensaje Recibido
    with open(os.path.join(dir, seq), 'w') as file:
        json.dump(y, file)

    # Crear Archivo .json con los datos del mensaje Recibido
    with open(os.path.join(dir, "demo"), 'w') as file:
        json.dump(y, file)

async def error_cb(e):
    print("Error:", e)

async def run(loop):

    #

    nc = NATS()
    sc = STAN()

    options = {
        "servers": ["nats://192.168.100.228:4222"],
        "io_loop": loop,
        "error_cb": error_cb
    }

    await nc.connect(**options)

    # Start session with NATS Streaming cluster using
    # the established NATS connection.
    await sc.connect("vsblty-cluster", "client-1235487854", nats=nc)

    async def cb(msg):

        task1 = await loop.create_task(ApiRequest())

        #task2 = await loop.create_task(JsonFrameProcess(msg.seq))

        
        
        # Mostrar por consola mensaje y Data
        #print("Received a message (seq={}): {}".format(msg.seq, msg.data))

        # Secuencia Mensaje
        #print(str(msg.seq))

        #/////////////////////////////////////////////////////////
        # Datos para Guardar Mensaje en Formato JSon
        #/////////////////////////////////////////////////////////
        # Ruta del Archivo donde se guardaran los archivos Json
        dir = 'C:/File-Nats/VSBLTY-DATA-TEMP'  

        # Date
        now = datetime.now()
        timestampStr = now.strftime("%d-%b-%Y %H%M%S")

        # Estructura para el Nombre del Archivo
        file_name = str(msg.seq) +" - "+ str(timestampStr) + " - Sensor-Processor - " + Hostname +".json"

        # Decode UTF-8 bytes mensaje Recibido 
        # to double quotes to make it valid JSON
        JsonNats = msg.data.decode('utf8').replace("'", '"')

        # mensaje es formatted JSON
        mensaje = json.loads(JsonNats)

        # Encoded Json Mensaje
        data_string = json.dumps(mensaje)

        # Decoded Json Mensaje
        decoded = json.loads(data_string)
        
        # Data
        HostnamePublisher = str(decoded["Hostname"])
        ChannelPublisher = str(decoded["Channel"])
        TypePublisher  = str(decoded["Type"])
        Data = decoded["Data"]
        Temp = str(decoded["Temp"])
        FrameTimestamp = str(decoded["FrameTimestamp"])

        # Secuencia Mensaje
        print ("Message: ", str(msg.seq))
        """ print ("   - Hostname-Publisher: ", HostnamePublisher)
        print ("   - Channel-Publisher: ", ChannelPublisher)
        print ("   - Type-Publisher: ", TypePublisher)
        print ("   - Temp Revived: ", Temp)
        print ("   - FrameTimestamp: ", FrameTimestamp) """

        # Crear Archivo .json con los datos del mensaje Recibido
        with open(os.path.join(dir, file_name), 'w') as file:
            json.dump(mensaje, file)

        # decodificar Imagen recibida
        Imagen = base64.decodestring(Data)
        Imagen = bytearray (Imagen)

        # ///////////////////////////////////////////////
        # reques Api Vsblty
        # ///////////////////////////////////////////////
        
        DataFrameProcess = (str(task1))
        type (DataFrameProcess)
        print (DataFrameProcess)

        # mensaje es formatted JSON
        DataFrameProcess = json.loads(task1)

        # Encoded Json Mensaje
        data_string_Frame = json.dumps(DataFrameProcess)
        print (data_string_Frame)

        # Decoded Json Mensaje
        decoded_Data = json.loads(data_string_Frame)
        print (decoded_Data)

        messageData = str(decoded_Data["message"])
        print (messageData)

        

    # Subscribe to get all messages from the beginning.
    await sc.subscribe("VSBLTY-DATA-TEMP", start_at='first', cb=cb)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()