#! /usr/bin/env python3

import rospy, sys
from r6g_steppermotor.msg import CurrentPose
from r6gPoints import PointData


def readCSV():
	"""Inicialización de nodo y construcción de tipo de mensaje"""
	rospy.init_node('ReadCSV', anonymous = True)
	pub = rospy.Publisher('CurrentPose', CurrentPose, queue_size = 100)
	rate = rospy.Rate(5) #Frecuencia de publicación
	r6g = CurrentPose()
	r6g.position = [0]*6
	r6g.name = ['Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6']
	recurrencia = 0
	count = 0
	sizeCSV = 0
	while not rospy.is_shutdown():
		r6g.position, r6g.endEffector, lineas = pose.GetLast(r6g.position)
		if sizeCSV == lineas and lineas != 2 and recurrencia == 0: 
			pub.publish(r6g)
			recurrencia += 1
			pose.Remake()
		if sizeCSV == lineas:
			recurrencia = 2
		else: 
			recurrencia = 0
		sizeCSV = lineas
		rate.sleep()

if __name__ == '__main__':
	try:
		pose = PointData(sys.argv[1])
		readCSV()
	except rospy.ROSInterruptException:
		pass
