# OpenCV
import cv2

# Time
from datetime import datetime

cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
count = 0

while True:
    ret,frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceClassif.detectMultiScale(gray, 1.3, 5)

    #Recorrer cada cara detectada
    for (x,y,w,h) in faces:
    # Dibuijar rectangulo
        cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
    cv2.imshow('frame',frame)

    # Timestamp por cada Frame
    count = count +1
    now = datetime.now()
    timestampStr = now.strftime("%Y-%b-%d %H.%M.%S.%f")
    cv2.imwrite('C:/File-Nats/Face/Face_{}_{}.jpg'.format(count, timestampStr),frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()