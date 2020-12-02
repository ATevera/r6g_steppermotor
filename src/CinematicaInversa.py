#!/usr/bin/env python3

from __future__ import print_function
from six.moves import input

import sys, copy, rospy, moveit_commander
from moveit_msgs.msg import OrientationConstraint, Constraints, CollisionObject
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list

from geometry_msgs.msg import PoseStamped
from r6g_steppermotor.msg import TargetPose

import math

def AnglesCalculation(target):
	moveit_commander.roscpp_initialize(sys.argv)
	robot = moveit_commander.RobotCommander()
	scene = moveit_commander.PlanningSceneInterface()
	r6g = moveit_commander.MoveGroupCommander("r6g_um")
	r6g.set_planner_id("BFMT")
	r6g.set_planning_time(3)
	r6g.allow_replanning(True)
	r6g.set_pose_reference_frame('Base')
	r6g.set_goal_position_tolerance(0.01)
	r6g.set_goal_orientation_tolerance(0.01)
	r6g.set_num_planning_attempts(3)
	pose_target = geometry_msgs.msg.Pose()
	#pose_target.header.frame_id = "Base"
	coordinates = [0]*3

	coordinates[0] = target.posicion[0]/100
	coordinates[1] = target.posicion[1]/100
	coordinates[2] = target.posicion[2]/100
	pose_target.orientation.x = target.orientacion[0]
	pose_target.orientation.y = target.orientacion[1]
	pose_target.orientation.z = target.orientacion[2]
	pose_target.orientation.w = target.orientacion[3]
	"""
	xyz = [0]*3
	for x in range(3):
	xyz[x] = target.posicion[x]/100
	"""
	r6g.set_start_state_to_current_state()
	target = r6g.set_position_target(coordinates)
	print(type(target))
	#r6g.set_position_target(xyz)
	#constraints = Constraints()
	#constraints.orientation_constraints = []
	#r6g.set_path_constraints(constraints)
	plan = r6g.plan()
	rospy.sleep(5)
	#r6g.execute(plan)
	r6g.go(wait = True)
	joints = r6g.get_current_joint_values()
	#print(planeacion)
	print(joints)
	#print(type(planeacion))
	r6g.stop()
	r6g.clear_pose_targets()

def InverseKinematics():
	rospy.init_node('CinematicaInversa', anonymous = True)
	rospy.Subscriber('TargetPose', TargetPose, AnglesCalculation)
	rospy.spin()

if __name__ == '__main__':
	try:
		InverseKinematics()
	except rospy.ROSInterruptException:
		pass
