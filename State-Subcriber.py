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
print('Runing... State-Manager - Nats Subscriber')


async def error_cb(e):
    print("Error:", e)

async def run(loop):
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
    await sc.connect("vsblty-cluster", "client-123548dsdf7854", nats=nc)

    async def cb(msg):
        # Mostrar por consola mensaje y Data
        #print("Received a message (seq={}): {}".format(msg.seq, msg.data))

        # Secuencia Mensaje
        print(str(msg.seq))
        print(str(msg.data)[:10])

        # Decode UTF-8 bytes mensaje Recibido 
        # to double quotes to make it valid JSON
        JsonNats = msg.data.decode('utf8').replace("'", '"')
        print (JsonNats[:10])

        


        dir = 'C:/File-Nats/State-Manager'  

        # Date
        now = datetime.now()
        timestampStr = now.strftime("%d-%m-%Y %H%M%S")

        # Build Json Mensaje 
        ChannelNats = 'VSBLTY-DATA-TEMP'
        data = {}
        data['Hostname'] = "Hostname"
        data['Channel'] = ChannelNats
        data['Type'] = 'Publisher'

        # Estructura para el Nombre del Archivo
        file_name = str(msg.seq) + " - [State-Manager] - " + str(timestampStr)  + ".json"

        # Crear Archivo .json con los datos del mensaje Recibido
        with open(os.path.join(dir, file_name), 'w') as file:
            json.dump(JsonNats, file)

    # Subscribe to get all messages from the beginning.
    await sc.subscribe("VSBLTY-DATA-FACE", start_at='first', cb=cb)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()