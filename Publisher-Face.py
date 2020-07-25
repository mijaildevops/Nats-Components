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

#///////////////////////////////////////////
# Hostname
#///////////////////////////////////////////
Hostname = socket.gethostname()
print('Runing... Nats Publisher')

def GetFrameCamera ():
    
    # Inicializar Camara 
    cap = cv2.VideoCapture(0)
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
    # Frame Request API- vsblty
    #//////////////////////////////////////////////////////////
    #Create a object with byte array of file. Only needed if image is in a OpenCV image. If it is just a byte[] file it can be posted directly
    is_success, im_buf_arr = cv2.imencode(".jpg", frame)
    byte_im = im_buf_arr.tobytes()
    
    #Place the file in the files array for the post method
    files = {'file': byte_im}

    #POST to API
    url = "http://openvino-api.vsblty.support:8099/process?raw"
    r=requests.post(url,files=files)

    #Analisis the results
    FrameAnalisis = str(r.content.decode())

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
    cv2.imwrite('C:/File-Nats/Face/{}.jpg'.format(timestampStr),frame)

    # destruir objeto con  el Frame
    cap.release()
    cv2.destroyAllWindows()

    DataFrame = [timestampStr,Image64, FrameAnalisis]

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
        ChannelNats = 'Face-Detection'
        data = {}
        data['Channel'] = ChannelNats
        data['Date'] = str(datetime.now())
        data['Hostname'] = Hostname
        data['Frame'] = str(Frame[1])
        data['timestampFrame'] = str(Frame[0])
        #data['FrameAnalisis'] = str(Frame[2])
        
        
        # Definir Channel y Mensaje
        await sc.publish(ChannelNats, bytes(str(data), 'utf8'))
        # Sleep 
        await asyncio.sleep(1, loop=loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
