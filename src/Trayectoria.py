#! /usr/bin/env python3

import rospy, csv, math, sys
import numpy as np
from sensor_msgs.msg import JointState

def InitCSVFile():
	with open(pathCSV, 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

def VerificarUltimoEstado(position):
	"""Verificar el último estado del robot en el archivo CSV para evitar sobreecribir datos"""
	actualPose = []
	with open(pathCSV, newline = '') as csvfile:
		verificador = csv.reader(csvfile, delimiter = ',', quotechar = '|')
		for angulos in verificador:
			actualPose = angulos
		index = 0
		comparador = True
		for joint in actualPose:
			if index < 6: comparador = float(joint) == round(math.degrees(position[index]),4) and comparador
			index += 1
	if len(actualPose) == 0 : comparador = False
	return comparador

def toCSV(data):
	"""Enviar ángulos a archivo CSV para su próxima lectura y envío mediante el puerto serial"""
	if not (VerificarUltimoEstado(data.position)):
		#rospy.loginfo("Trayectoria: %s","Escribiendo nueva pose para el robot en archivo CSV ... ")
		estado = ""
		rowValues = np.array([])
		for angulo in data.position:
			angulo = round(math.degrees(angulo),4)
			estado += "{}, ".format(angulo)
			rowValues = np.append(rowValues,'{}'.format(angulo))
		rowValues = np.append(rowValues,'0')		
		with open(pathCSV, 'a') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
			writer.writerow(rowValues)
	

def trayectoria():
	rospy.init_node('Trayectoria', anonymous=True)
	rospy.Subscriber("joint_states", JointState, toCSV)
	rospy.spin()

if __name__ == '__main__':
	pathCSV = sys.argv[1]
	InitCSVFile()
	trayectoria()
