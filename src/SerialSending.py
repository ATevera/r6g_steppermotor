#! /usr/bin/env python3
import rospy
from r6g_steppermotor.msg import CurrentPose
import serial, time, sys

def SendData(name, target):
	"""Envío de datos por el puerto serial con estructura JSON"""
	i = 0
	while not esp32.readable():
		i += 1
	rospy.loginfo("SerialSending: %s", target)
	esp32.write(target.encode())

def ToJSONFile(robot):
	"""Construcción del mensaje en formato JSON"""
	
	target = "{"
	estado = ""
	i = 0

	comparative = True

	for grado in robot.position:
		comparative = grado == valuesDoF[i] and comparative 
		valuesDoF[i] = grado
		target += "\"J{}\": {},".format(i+1,grado)
		estado += "J{}: {} ".format(i+1,grado)
		i += 1
	target += "\"EF\": {}".format(robot.endEffector)
	estado += "EF: {}".format(robot.endEffector)
	target += "}"
	PosName = "Position"
	if not comparative:
		SendData(PosName,target)

def SerialSending():
	"""Inicialización del nodo suscriptor"""
	rospy.init_node('SerialSending', anonymous=True)
	rospy.Subscriber("CurrentPose", CurrentPose, ToJSONFile)
	print('Nodo creado con Éxito')
	rospy.spin()

#Inicialización del puerto serie
port = sys.argv[1]

esp32 = serial.Serial(port, 115200)
esp32.setDTR = True
print('Puerto serial iniciado en {}'.format(port))
valuesDoF = [0, -71, 75, 0, 0, 0]

if __name__ == '__main__':
	try:
		SerialSending()
	except rospy.ROSInterruptException:
		esp32.close()

