# Nats
import asyncio
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from datetime import datetime
# Hostname
import socket 
# Base64
import base64
from base64 import b64encode

#///////////////////////////////////////////
# Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('Runing... Nats Publisher')

#///////////////////////////////////////////
# Convertir imagen a base64
#///////////////////////////////////////////
with open("test.jpg", "rb") as imageFile:
    # Imagen en Bytes
    Image64 = base64.b64encode(imageFile.read())
    # Imagen de Bytes a String
    Image64 =Image64.decode('utf-8')

#///////////////////////////////////////////
# Capturar Erro de Conexion al Nats
# #/////////////////////////////////////////// 
async def error_cb(e):
    print("Error:", e)

# Funcion Nats Publisher
async def run(loop):
    nc = NATS()
    sc = STAN()
    
    options = {
        "servers": ["nats://100.97.218.207:4222"],
        "io_loop": loop,
        "error_cb": error_cb
    }
    print ("Sever: ", options["servers"])

    # variables de Conexion Nats Server
    await nc.connect(**options)

    # First connect to NATS, then start session with NATS Streaming.
    # the established NATS connection.
    await sc.connect("vsblty-cluster", Hostname, nats=nc)

    # Periodically send a message Cada Segundo
    while True:

        # Build Json Mensaje 
        ChannelNats = 'Face-Detection'
        data = {}
        data['Channel'] = ChannelNats
        data['Date'] = str(datetime.now())
        data['Frame'] = Image64
        data['Hostname'] = Hostname
        
        # Definir Channel y Mensaje
        await sc.publish(ChannelNats, bytes(str(data), 'utf8'))
        # Sleep 
        await asyncio.sleep(1, loop=loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()