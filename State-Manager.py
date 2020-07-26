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
        print('Bites: ',str(msg.data)[:200])

        # Decode UTF-8 bytes mensaje Recibido 
        # to double quotes to make it valid JSON
        JsonNats = msg.data.decode('utf8').replace("'", '"')
        print('')
        # Ver informacion en formato Json
        #print (type(JsonNats))

        # para corregir erro serrelizando Json Remplazo cadena 
        JsonNatsRemplace =  JsonNats.replace('license": True, "manager": True, "', 'license": "True", "manager": "True", "')
        
        # Serelizando Data
        parsed_json = (json.loads(JsonNatsRemplace))
        #print(json.dumps(parsed_json, indent=4, sort_keys=True))

        # Analisi
        DistanceEngage = 1.1
        TempLimit = 98.6
        TempRangoHigh = TempLimit + 0.5

        # datos Secuencia
        FrameTimestampId = parsed_json["FrameTimestampId"]
        SecuenciaMsg = parsed_json["SecuenciaMsg"]
        Data = parsed_json["Data"]
        TempPerson = parsed_json["Temp"]
        
        # Face detection
        confidence = parsed_json["FaceDetection"]["results"]["FaceDetector"]["detections"][0]["FaceDetector"]["confidence"]
        DistancePerson = parsed_json["FaceDetection"]["results"]["FaceDetector"]["detections"][0]["FaceIdentifier"]["distance"]
        AgeGenderDetector = parsed_json["FaceDetection"]["results"]["FaceDetector"]["detections"][0]["AgeGenderDetector"]
        left_eye = parsed_json["FaceDetection"]["results"]["FaceDetector"]["detections"][0]["LandmarksDetector"]["left_eye"]
        right_eye = parsed_json["FaceDetection"]["results"]["FaceDetector"]["detections"][0]["LandmarksDetector"]["right_eye"]

        # Print data
        #print(Data)
        print(FrameTimestampId)
        print(TempPerson)
        print(SecuenciaMsg)
        print(AgeGenderDetector)
        print(confidence)
        print(DistancePerson)
        print(left_eye)
        print(right_eye)

        print (' ---- Start Analisys ----')
        print ("TempLimit: ", TempLimit)
        print ("TempRange: ", TempRangoHigh)
        print ("Temp (+0.5): ", TempPerson)

        if (float(DistancePerson) < float(DistanceEngage)):
            if (float(TempPerson) < float(TempRangoHigh)):
                State = 'Pass'
                StateDescription = 'Detected Person Has (Normal) Body Temperature'
            else:
                State = 'Fail'
                StateDescription = 'The detected person has a higher temperature than the configured one'
        else:
            State = 'Fail'
            StateDescription = 'Detected Person is not at the Minimum Distance for analysis'

        # Json Data
        data = {}
        data['FrameTimestampId'] = str(FrameTimestampId)
        data['SecuenciaMsg'] = str(SecuenciaMsg)
        data['Data'] = str(Data)
        data['TempPerson'] = str(TempPerson)

        data['TempLimit'] = str(TempLimit)
        data['TempMax'] = str(TempRangoHigh)
        data['DistanceEngage'] = str(DistanceEngage)

        data['Confidence'] = str(confidence)
        data['DistancePerson'] = str(DistancePerson)
        #data['AgeGenderDetector'] = str(AgeGenderDetector)
        data['Left_eye'] = str(left_eye)
        data['Right_eye'] = str(right_eye)

        data['State'] = str(State)
        data['StateDescription'] = str(StateDescription)

        #////////////////////////////////////////////////////////////////
        # Save json  Subcriber
        #////////////////////////////////////////////////////////////////
        dir = 'C:/File-Nats/State-Manager/Subscriber'  
        # Date
        now = datetime.now()
        timestampStr = now.strftime("%d-%m-%Y %H%M%S")

        # Estructura para el Nombre del Archivo
        file_name = str(msg.seq) + " - [State-Manager - [Subscriber] - " + str(timestampStr)  + ".json"

        # Crear Archivo .json con los datos del mensaje Recibido
        with open(os.path.join(dir, file_name), 'w') as file:
            json.dump(parsed_json, file)

        #////////////////////////////////////////////////////////////////
        # Save json  Publisher
        #////////////////////////////////////////////////////////////////
        dir = 'C:/File-Nats/State-Manager/Publisher'  
        # Date
        now = datetime.now()
        timestampStr = now.strftime("%d-%m-%Y %H%M%S")

        # Estructura para el Nombre del Archivo
        file_name = str(msg.seq) + " - [State-Manager] - [Publisher] - " + str(timestampStr)  + ".json"

        # Crear Archivo .json con los datos del mensaje Recibido
        with open(os.path.join(dir, file_name), 'w') as file:
            json.dump(data, file)

         # Publicar Mensaje con el resultado en el canal VSBLTY-DATA-FACE
        ChannelNatsPublisher = 'VSBLTY-DATA-VISUALIZATION'
        # Definir Channel y Mensaje
        await sc.publish(ChannelNatsPublisher, bytes(str(data), 'utf8'))
        # Sleep 


    # Subscribe to get all messages from the beginning.
    await sc.subscribe("VSBLTY-DATA-FACE", start_at='first', cb=cb)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()