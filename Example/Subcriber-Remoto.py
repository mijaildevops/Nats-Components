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

#///////////////////////////////////////////
# Get Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('Runing... Nats Subscriber')


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
    await sc.connect("vsblty-cluster", "client-1235487854", nats=nc)

    async def cb(msg):
        # Mostrar por consola mensaje y Data
        #print("Received a message (seq={}): {}".format(msg.seq, msg.data))

        # Secuencia Mensaje
        print(str(msg.seq))

        #/////////////////////////////////////////////////////////
        # Datos para Guardar Mensaje en Formato JSon
        #/////////////////////////////////////////////////////////
        # Ruta del Archivo donde se guardaran los archivos Json
        dir = 'C:/File-Nats/Nats-Mensajes'  

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

        # Crear Archivo .json con los datos del mensaje Recibido
        with open(os.path.join(dir, file_name), 'w') as file:
            json.dump(mensaje, file)

    # Subscribe to get all messages from the beginning.
    await sc.subscribe("VSBLTY-DATA-TEMP", start_at='first', cb=cb)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()