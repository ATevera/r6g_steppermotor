#! /usr/bin/env python3

import rospy, csv, sys
from r6g_steppermotor.msg import CurrentPose

def GetLastPose(position):
	"""Obtiene la última pose registrada en el archivo CSV, así como el estado del efector final para publicarlo en el tópico definido"""
	tempPose = [0]*6
	LastPose = [0]*6
	rows = 1
	with open(pathCSV, newline = '') as csvfile:
		lector = csv.reader(csvfile, delimiter = ',', quotechar = '|')
		for pose in lector:
			tempPose = pose
			rows += 1
		for i in range(6):
			LastPose[i] = float(tempPose[i])
		index = 0
	return LastPose, int(tempPose[-1]), rows

def readCSV():
	"""Inicialización de nodo y construcción de tipo de mensaje"""
	rospy.init_node('ReadCSV',anonymous = True)
	pub = rospy.Publisher('CurrentPose', CurrentPose, queue_size = 100)
	rate = rospy.Rate(10) #Frecuencia de publicación
	r6g = CurrentPose()
	r6g.position = [0]*6
	r6g.name = ['Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6']
	recurrencia = 0
	count = 0
	sizeCSV = 0
	while not rospy.is_shutdown():
		r6g.position, r6g.endEffector, lineas = GetLastPose(r6g.position)
		if sizeCSV == lineas and lineas != 2 and recurrencia == 0: 
			pub.publish(r6g)
			recurrencia += 1
		if sizeCSV == lineas:
			recurrencia = 2
		else: 
			recurrencia = 0
		sizeCSV = lineas
		rate.sleep()

if __name__ == '__main__':
	try:
		pathCSV = sys.argv[1]
		readCSV()
	except rospy.ROSInterruptException:
		pass
