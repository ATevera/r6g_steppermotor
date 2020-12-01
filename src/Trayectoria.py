#! /usr/bin/env python3

import rospy, math, sys
import numpy as np
from sensor_msgs.msg import JointState
from r6gPoints import PointData

def toCSV(data):
	"""Enviar ángulos a archivo CSV para su próxima lectura y envío mediante el puerto serial"""
	if not (pose.Compare(data.position)):
		#rospy.loginfo("Trayectoria: %s","Escribiendo nueva pose para el robot en archivo CSV ... ")
		estado = ""
		rowValues = np.array([])
		for angulo in data.position:
			angulo = round(math.degrees(angulo),4)
			estado += "{}, ".format(angulo)
			rowValues = np.append(rowValues,'{}'.format(angulo))
		rowValues = np.append(rowValues,'0')
		pose.Write(rowValues)	

def trayectoria():
	rospy.init_node('Trayectoria', anonymous=True)
	rospy.Subscriber("joint_states", JointState, toCSV)
	rospy.spin()

if __name__ == '__main__':
	pose = PointData(sys.argv[1])
	pose.Remake()
	trayectoria()
