#  Flask
from flask import Flask, request
from flask import render_template
from flask import jsonify
# Cors
from flask_cors import CORS
# Json
import json
import os

# Cors access
#app=Flask(__name__,template_folder='templates')
app=Flask(__name__,template_folder='templates')
cors = CORS(app)

#//////////////////////////////////////////////////////////////////////////
# Index
#//////////////////////////////////////////////////////////////////////////
@app.route('/')
def home():

    dir = 'C:/File-Nats/Visualization/Data/Data.json'
    json_data = json.loads(open(dir).read())

    Data = json_data["Data"]
    State = json_data["State"]
    Mensaje = json_data["StateDescription"]

    titulo = "View"
    usuario = {'App': 'Kiosk.com'}
    div = "Pass"
    return render_template('index.html',
                           titulo=titulo,
                           usuario=usuario,
                           div=div,
                            Data='<img src="data:image/png;base64,' + Data + '" width="45%" height="45%" alt="base64 test">',
                             State=State,
                              Mensaje=Mensaje) 

#//////////////////////////////////////////////////////////////////////////
# Api Data
#//////////////////////////////////////////////////////////////////////////
@app.route('/Data')
def Data():
    dir = 'C:/File-Nats/Visualization/Data/Data.json'
    json_data = json.loads(open(dir).read())
    return jsonify(json_data)

app.run(host='192.168.100.102', port=6080, debug=True)