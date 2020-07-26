# OpenCV
import cv2
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
# Time
from datetime import datetime
import time
# Request
import requests
# Ramdon temp
import random

#///////////////////////////////////////////
# Temperatura
TempRandom = [95, 95.90, 96.44, 96.80, 97.34, 97.88, 98.42, 98.78, 99.14, 99.86, 100.76, 101.40, 102.02, 101.66, 102.20, 102.74, 103.28, 109.90, 104.00]
#///////////////////////////////////////////

#///////////////////////////////////////////
# Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('Runing... Nats Publisher')

def GetFrameCamera ():
    
    # Inicializar Camara 
    #cap = cv2.VideoCapture(0) #USB
    cap = cv2.VideoCapture('http://100.97.218.207/camara/low/Correa%20Cloud.jpg') #IP
    # modelo de deteccion
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    
    # caprurar Frame
    ret,frame = cap.read()

    #//////////////////////////////////////////////////////////
    # Convertir Frame a (bytes)
    #//////////////////////////////////////////////////////////
    ret, buffer = cv2.imencode('.jpg', frame)
    ImagenBytes = base64.b64encode(buffer)
    # Convertir Frame from bytes to Base64
    Image64 =ImagenBytes.decode('utf-8')

    #//////////////////////////////////////////////////////////
    # procesar Frame para detectar faces
    #//////////////////////////////////////////////////////////
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceClassif.detectMultiScale(gray, 1.3, 5)

    #Recorrer cada cara detectada
    for (x,y,w,h) in faces:
    # Dibuijar rectangulo
        cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
    
    # Mostrar Ventana Con la camara 
    #cv2.imshow('frame',frame)

    # Timestamp por cada Frame
    now = datetime.now()
    timestampStr = now.strftime("%Y-%m-%d %H.%M.%S.%f")
    # Guardar Imagen
    #cv2.imwrite('C:/File-Nats/Face/{}.jpg'.format(timestampStr),frame)

    # destruir objeto con  el Frame
    cap.release()
    cv2.destroyAllWindows()

    DataFrame = [timestampStr,Image64]

    return DataFrame

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

        #Get Frame 
        Frame = GetFrameCamera()

        # Build Json Mensaje 
        ChannelNats = 'VSBLTY-DATA-TEMP'
        data = {}
        data['Hostname'] = Hostname
        data['Channel'] = ChannelNats
        data['Type'] = 'Publisher'
        data['Data'] = str(Frame[1])
        data['Temp'] = str(random.choice(TempRandom))
        data['FrameTimestamp'] = str(Frame[0])       
        
        # Definir Channel y Mensaje
        await sc.publish(ChannelNats, bytes(str(data), 'utf8'))
        # Sleep 
        await asyncio.sleep(1, loop=loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
