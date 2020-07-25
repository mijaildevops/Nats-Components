import cv2

import requests

 

#JUST to get the image into memory. Your code will probably already have a file in memory from the Dermalog API. You don't need to write to disk. 

im = cv2.imread('pruitt.png')

 

#Create a object with byte array of file. Only needed if image is in a OpenCV image. If it is just a byte[] file it can be posted directly

is_success, im_buf_arr = cv2.imencode(".jpg", im)

byte_im = im_buf_arr.tobytes()

 

#Place the file in the files array for the post method

files = {'file': byte_im}

 

#POST to API

url = "http://openvino-api.vsblty.support:8099/process?raw"

r=requests.post(url,files=files)

 

#Print the results

print(str(r.content.decode()))