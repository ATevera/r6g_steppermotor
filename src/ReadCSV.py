#! /usr/bin/env python3

import csv
import rospy
from r6g_steppermotor.msg import CurrentPose

import sys

pathCSV = sys.argv[1]
#pathCSV = 'src/csvfiles/joints_values.csv'

def GetLastPose(position):
	tempPose = [0]*6
	LastPose = [0]*6
	with open(pathCSV, newline = '') as csvfile:
		lector = csv.reader(csvfile, delimiter = ',', quotechar = '|')
		for pose in lector:
			tempPose = pose
		for i in range(6):
			LastPose[i] = float(tempPose[i])
		index = 0
		comparador = True
		for joint in LastPose:
			if index < len(position): comparador = joint == position[index] and comparador
			index += 1
	return comparador, LastPose, int(LastPose[-1])

def readCSV():
	rospy.init_node('ReadCSV',anonymous = True)
	pub = rospy.Publisher('CurrentPose', CurrentPose, queue_size=100)
	print('Lector de CSV inicializado')
	rate = rospy.Rate(10) #Frecuencia de publicación
	r6g = CurrentPose()
	r6g.position = [0]*6
	r6g.name = ['Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6']
	recurrencia = 0
	count = 0
	while not rospy.is_shutdown():
		estado, r6g.position, r6g.endEffector = GetLastPose(r6g.position)
		if estado:  recurrencia += 1
		else: recurrencia = 0
		if recurrencia == 2:
			count += 1
			pub.publish(r6g)
			rospy.loginfo("ReadCSV: %s","Publicando en Esp32 . . . x{}".format(count))
			#rate.sleep()
			with open(pathCSV, 'w') as csvfile:
				writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

if __name__ == '__main__':
	try:
		readCSV()
	except rospy.ROSInterruptException:
		pass
