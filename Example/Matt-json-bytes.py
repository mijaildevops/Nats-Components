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
# base64
import base64
image = open('test.jpg', 'rb')
image_read = image.read()
image_64_encode = base64.encodestring(image_read)
print (image_64_encode[:6])
image_64_decode = base64.decodestring(image_64_encode) 
print (image_64_decode[:6])
print (type(image_64_decode))
""" image_result = open('deer_decode.gif', 'wb') # create a writable image and write the decoding result
image_result.write(image_64_decode) """

 

#Place the file in the files array for the post method

files = {'file': image_64_decode}

 

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
