#!/usr/bin/env python3
import rospy, sys
import cv2 as cv
import numpy as np
from r6g_steppermotor.msg import TargetPose
from r6gPoints import PointData


#creación de trackbars
def nothing(val):
    pass

def makeTrackBars():
	cv.namedWindow('Color a detectar minimos')
	cv.createTrackbar('Hue Min','Color a detectar minimos',0,360,nothing)
	cv.createTrackbar('Saturación Min','Color a detectar minimos',0,255,nothing)
	cv.createTrackbar('Valor Min','Color a detectar minimos',0,255,nothing)
	cv.createTrackbar('Area','Color a detectar minimos',0,10000,nothing)
	cv.createTrackbar('Blur','Color a detectar minimos',1,50,nothing)

	cv.namedWindow('Color a detectar maximos')
	cv.createTrackbar('Hue Max','Color a detectar maximos',0,360,nothing)
	cv.createTrackbar('Saturación Max','Color a detectar maximos',0,255,nothing)
	cv.createTrackbar('Valor Max','Color a detectar maximos',0,255,nothing)

	#set con la detección en color
	cv.setTrackbarPos('Hue Min','Color a detectar minimos',80)
	cv.setTrackbarPos('Hue Max','Color a detectar maximos',119)
	cv.setTrackbarPos('Saturación Min','Color a detectar minimos',61)
	cv.setTrackbarPos('Saturación Max','Color a detectar maximos',255)
	cv.setTrackbarPos('Valor Min','Color a detectar minimos',99)
	cv.setTrackbarPos('Valor Max','Color a detectar maximos',255)
	cv.setTrackbarPos('Area','Color a detectar minimos',400)
	cv.setTrackbarPos('Blur','Color a detectar minimos',30)

def readTrackBars():
	h = cv.getTrackbarPos('Hue Min','Color a detectar minimos')
	s = cv.getTrackbarPos('Saturación Min','Color a detectar minimos')
	v = cv.getTrackbarPos('Valor Min','Color a detectar minimos')
	a = cv.getTrackbarPos('Area','Color a detectar minimos')
	b = cv.getTrackbarPos('Blur','Color a detectar minimos')
	H = cv.getTrackbarPos('Hue Max','Color a detectar maximos')
	S = cv.getTrackbarPos('Saturación Max','Color a detectar maximos')
	V = cv.getTrackbarPos('Valor Max','Color a detectar maximos')
	return h, s, v, H, S, V, a, b

def ordenar_puntos(puntos):
	n_puntos = np.concatenate([puntos[0], puntos[1], puntos[2], puntos[3]]).tolist()
	y_order = sorted(n_puntos, key = lambda n_puntos: n_puntos[1])
	x1_order = y_order[:2]
	x1_order = sorted(x1_order, key = lambda x1_order: x1_order[0])
	x2_order = y_order[2:4]
	x2_order = sorted(x2_order, key = lambda x2_order: x2_order[0])
	return [x1_order[0], x1_order[1], x2_order[0], x2_order[1]]

def roi(image, ancho, alto):
	imagen_alineada = None
	gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
	_, th = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
	cnts = cv.findContours(th, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
	cnts = sorted(cnts, key = cv.contourArea, reverse = True)[:1]

	for c in cnts:
		epsilon = 0.01*cv.arcLength(c,True)
		approx = cv.approxPolyDP(c,epsilon,True)
		if len(approx) == 4:
			puntos = ordenar_puntos(approx)
			pts1 = np.float32(puntos)
			pts2 = np.float32([[0,0], [ancho,0], [0,alto], [ancho,alto]])
			M = cv.getPerspectiveTransform(pts1, pts2)
			imagen_alineada = cv.warpPerspective(image, M, (ancho,alto))
	return imagen_alineada

#creando dos imagenes de 100x300 pixeles con tres canales(BGR)
img1 = np.zeros((100,300,3), np.uint8)
img2 = np.zeros((100,300,3), np.uint8)
img1_hsv = cv.cvtColor(img1, cv.COLOR_BGR2HSV)
img2_hsv = cv.cvtColor(img2, cv.COLOR_BGR2HSV)

workspace = [245, 80] #Dimensiones en mm en y,x (ancho, alto)
aspect_ratio = workspace[0]/workspace[1] #ratio = ancho/alto
perspectiva_y = 720
perspectiva_x = int(perspectiva_y/aspect_ratio)

def Detector():
	"""Inicialización de nodo y construcción de tipo de mensaje"""
	rospy.init_node('Detector',anonymous = True)
	pub = rospy.Publisher('TargetPose', TargetPose, queue_size = 100)
	rate = rospy.Rate(5) #Frecuencia de publicación
	pieza = TargetPose()
	#iniciar camara
	cap = cv.VideoCapture(0)
	makeTrackBars()
	pose = PointData(sys.argv[1])
	pose_revision = [0.0, 0.0, 0.0, 0.0, 90.0, 0.0]

	#Offset entre frame world y frame cámara
	offset_x = 185
	offset_y = 120
	
	#Altura pieza a detectar
	pieza.camaraFrame = [0.0, 0.0, 10.0]
	pieza.posicion = [0.0]*3
	pieza.orientacion = [-3.799e-06, 1.0, -3.40596e-05, 1.39966e-05]

	while not rospy.is_shutdown():
		ret, frame = cap.read()
		#guardando la posición de los trackbars en variables
		hl, sl, vl, hh, sh, vh, a, blur = readTrackBars()
		#creando imagenes con la posición de los trackbars
		img1_hsv[:] = [hl,sl,vl]
		img2_hsv[:] = [hh,sh,vh]
		img1 = cv.cvtColor(img1_hsv, cv.COLOR_HSV2BGR)
		img2 = cv.cvtColor(img2_hsv, cv.COLOR_HSV2BGR)
		#Creación de los array con los limites HSV obtenidos de los trackbars
		rango_l = np.array([hl,sl,vl])
		rango_h = np.array([hh,sh,vh])
		#Proceso de transferencia de Perspectiva
		enfoque_ws = roi(frame, ancho = perspectiva_y, alto = perspectiva_x)

		if enfoque_ws is not None and pose.Checking(pose_revision, 5):
			framehsv = cv.cvtColor(enfoque_ws, cv.COLOR_BGR2HSV)
			mask = cv.inRange(framehsv,rango_l,rango_h)
			blur = 2*blur +1
			#gauss = cv.GaussianBlur(mask, (blur,blur), 0
			masknot = cv.bitwise_not(mask)
			maskcolor = cv.bitwise_and(enfoque_ws, enfoque_ws,mask = mask)
			maskblack = cv.bitwise_and(enfoque_ws, enfoque_ws, mask = masknot)
			maskblur = cv.GaussianBlur(maskblack, (blur,blur), 0)
			masksalida = cv.add(maskblur,maskcolor)
			#Encontrar contornos
			contornos,_ = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
			x_mm = 0
			y_mm = 0
			for i in range(len(contornos)) :
				area = cv.contourArea(contornos[i])
				if area > a :
					M = cv.moments(contornos[i])
					if (M["m00"] == 0): M["m00"] = 1
					x = int(M["m10"]/M["m00"])
					y = int(M['m01']/M['m00'])
					#Coordenada relativa en mm, intercambio de coordanadas para coincidencia con el marco de referencia del robot.
					y_mm = float(x * workspace[1]/perspectiva_x)
					x_mm = float(y * workspace[0]/perspectiva_y)
					cv.circle(masksalida, (x,y), 7, (0,255,0), -1)
					font = cv.FONT_HERSHEY_SIMPLEX
					cv.putText(masksalida, '{},{}'.format(int(x_mm),int(y_mm)),(x+30,y+30), font, 0.75,(0,255,0),1,cv.LINE_AA)
					cv.drawContours(masksalida,contornos[i],-1,(0,255,0),6)
			pieza.camaraFrame[0] = round(x_mm, 4)
			pieza.camaraFrame[1] = round(y_mm + 10, 4)
			pieza.posicion[0] = round(x_mm + offset_x, 4)
			pieza.posicion[1] = round(y_mm - offset_y, 4)
			pieza.posicion[2] = round(pieza.camaraFrame[2] - 10, 4)
			pub.publish(pieza)
			cv.imshow('Real',masksalida)
			#cv.imshow('Mask',mask)
		if cv.waitKey(1) & 0xFF == ord('q') : break
		cv.imshow('frame', frame)
		#cv.imshow('Color a detectar minimos',img1)
		#cv.imshow('Color a detectar maximos',img2)
	cap.release()
	cv.destroyAllWindows()    

if __name__ == '__main__':
	try:
		Detector()
	except rospy.ROSInterruptException:
		cap.release()
		cv.destroyAllWindows()
        
