import cv2

import requests
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

 

#Print the results

respuesta = str(r.content.decode())

data = {}
data['Hostname'] = "Hostname-254"


dir = 'C:/File-Nats/VSBLTY-DATA-FACE'  

# Date
now = datetime.now()
timestampStr = now.strftime("%d-%b-%Y %H%M%S")

# Estructura para el Nombre del Archivo
file_name =" - " + str(timestampStr) + " - Sensor-Processor - .json"

# Decode UTF-8 bytes mensaje Recibido 
# to double quotes to make it valid JSON
#JsonNats = respuesta.data.decode('utf8').replace("'", '"')

# mensaje es formatted JSON
mensaje = json.loads(respuesta)

data['respuesta'] = mensaje



# Crear Archivo .json con los datos del mensaje Recibido
with open(os.path.join(dir, file_name), 'w') as file:
    json.dump(data, file)
