#! /usr/bin/env python3

import rospy
from r6g_steppermotor.msg import TargetPose

def ControlPose():
    rospy.init_node("ControlPose", anonymous = True)
    pub = rospy.Publisher('TargetPose', TargetPose, queue_size = 100)
    pose = TargetPose()
    pose.camaraFrame = [0.0]*3
    #pose.posicion = [0.0]*3
    #pose.orientacion = [0.0]*4

    posename = int(input("Seleccione pose del 1 al 3: "))

    if posename == 1:
        pose.posicion = [0.132247, 0, 0.214067]
        pose.orientacion = [0, 0.70709, 0, 0.707124]
    elif posename == 2:
        pose.posicion = [0.227503, 0, 0.26904]
        pose.orientacion = [0, 0.707131, 0, 0.707083]
    else:
        pose.posicion = [0.164053, 0, 0.204489]
        pose.orientacion = [0, 1, 0, 0]
    pub.publish(pose)
    """
    while not rospy.is_shutdown():
        for x in range(3):
            pose.posicion[x] = float(input('Valor en pos {}: '.format(x)))

        for x in range(4):
            pose.orientacion[x] =float(input('Valor en or {}: '.format(x)))
        pub.publish(pose)
    """

if __name__ == '__main__':
	try:
		ControlPose()
	except rospy.ROSInterruptException:
		pass
