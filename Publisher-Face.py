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

def GetFrameCamera ():
    
    # Inicializar Camara 
    cap = cv2.VideoCapture(0)
    # modelo de deteccion
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    
    # caprurar Frame
    ret,frame = cap.read()

    # Convertir Frame a (bytes)
    ret, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    # Convertir Frame from bytes to Base64
    Image64 =jpg_as_text.decode('utf-8')

    # procesar Frame para detectar faces
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

    DataFrame = [timestampStr,Image64]

    return DataFrame

Frame = GetFrameCamera()
for dato in Frame:
    print(dato)

