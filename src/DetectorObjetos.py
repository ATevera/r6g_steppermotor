from cv2 import cv2 as cv
import numpy as np

#iniciar camara 
cap=cv.VideoCapture(0)

#creación de trackbars
def nothing(val):
    pass

cv.namedWindow('Color a detectar minimos')
cv.createTrackbar('Hue Min','Color a detectar minimos',0,179,nothing)
cv.createTrackbar('Saturación Min','Color a detectar minimos',0,255,nothing)
cv.createTrackbar('Valor Min','Color a detectar minimos',0,255,nothing)
cv.createTrackbar('Area','Color a detectar minimos',0,10000,nothing)
cv.createTrackbar('Blur','Color a detectar minimos',1,50,nothing)

cv.namedWindow('Color a detectar maximos')
cv.createTrackbar('Hue Max','Color a detectar maximos',0,179,nothing)
cv.createTrackbar('Saturación Max','Color a detectar maximos',0,255,nothing)
cv.createTrackbar('Valor Max','Color a detectar maximos',0,255,nothing)

#set con la detección en color azul
cv.setTrackbarPos('Hue Min','Color a detectar minimos',5)
cv.setTrackbarPos('Hue Max','Color a detectar maximos',22)
cv.setTrackbarPos('Saturación Min','Color a detectar minimos',100)
cv.setTrackbarPos('Saturación Max','Color a detectar maximos',255)
cv.setTrackbarPos('Valor Min','Color a detectar minimos',100)
cv.setTrackbarPos('Valor Max','Color a detectar maximos',255)
cv.setTrackbarPos('Area','Color a detectar minimos',1000)
cv.setTrackbarPos('Blur','Color a detectar minimos',50)

#creando dos imagenes de 100x300 pixeles con tres canales(RGB)
img1 =np.zeros((100,300,3), np.uint8)
img2 =np.zeros((100,300,3), np.uint8)
img1_hsv = cv.cvtColor(img1, cv.COLOR_BGR2HSV)
img2_hsv = cv.cvtColor(img2, cv.COLOR_BGR2HSV)



while True:
    ret, frame=cap.read()

    #guardando la posición de los trackbars en variables
    hl = cv.getTrackbarPos('Hue Min','Color a detectar minimos') 
    sl = cv.getTrackbarPos('Saturación Min','Color a detectar minimos') 
    vl = cv.getTrackbarPos('Valor Min','Color a detectar minimos')  
    a = cv.getTrackbarPos('Area','Color a detectar minimos') 
    blur = cv.getTrackbarPos('Blur','Color a detectar minimos') 

    hh = cv.getTrackbarPos('Hue Max','Color a detectar maximos') 
    sh = cv.getTrackbarPos('Saturación Max','Color a detectar maximos') 
    vh = cv.getTrackbarPos('Valor Max','Color a detectar maximos')
   
    #creando imagenes con la posición de los trackbars
    img1_hsv[:] = [hl,sl,vl]
    img2_hsv[:] = [hh,sh,vh]
    img1 = cv.cvtColor(img1_hsv, cv.COLOR_HSV2BGR)
    img2 = cv.cvtColor(img2_hsv, cv.COLOR_HSV2BGR)

    #Creación de los array con los limites HSV obtenidos de los trackbars
    rango_l = np.array([hl,sl,vl]) 
    rango_h = np.array([hh,sh,vh]) 
    
    framehsv= cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask=cv.inRange(framehsv,rango_l,rango_h)
    blur = 2*blur +1
    #gauss = cv.GaussianBlur(mask, (blur,blur), 0)

    masknot = cv.bitwise_not(mask)
    maskcolor = cv.bitwise_and(frame,frame,mask= mask)
    maskblack = cv.bitwise_and(frame, frame, mask = masknot)
    maskblur = cv.GaussianBlur(maskblack, (blur,blur), 0)
    masksalida = cv.add(maskblur,maskcolor)
    

    #Encontrar contornos
    contornos,_=cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    
    for i in range(len(contornos)) :
        area = cv.contourArea(contornos[i])

        if area > a :
            
            M=cv.moments(contornos[i])
            if (M["m00"]==0): M["m00"]=1
            x = int(M["m10"]/M["m00"])
            y = int(M['m01']/M['m00'])
            cv.circle(masksalida, (x,y), 7, (0,255,0), -1)
            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(masksalida, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv.LINE_AA)

            cv.drawContours(masksalida,contornos[i],-1,(0,255,0),6)

    

    cv.imshow('Color a detectar minimos',img1)
    cv.imshow('Color a detectar maximos',img2)
    cv.imshow('Mask',mask)
    cv.imshow('Real',masksalida)

    if cv.waitKey(1) & 0xFF == ord('r'):
        break
cap.release()
cv.destroyAllWindows()    