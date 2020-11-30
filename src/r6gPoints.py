#! /usr/bin/env python3

import csv, math

class PointData:
	def __init__(self, path):
		self.path = path

	def Remake(self):
		with open(self.path, 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

	def GetLast(self, position):
		"""Obtiene la última pose registrada en el archivo CSV, así como el estado del efector final para publicarlo en el tópico definido"""
		tempPose = [0]*6
		LastPose = [0]*6
		rows = 1
		with open(self.path, newline = '') as csvfile:
			lector = csv.reader(csvfile, delimiter = ',', quotechar = '|')
			for pose in lector:
				tempPose = pose
				rows += 1
			for i in range(6):
				LastPose[i] = float(tempPose[i])
			index = 0
		return LastPose, int(tempPose[-1]), rows

	def Current(self, Target):
		"""Verifica que la pose sea la correcta para aplicar visión artificial"""
		tempPose = [0]*6
		verificador = True
		with open(self.path, newline = '') as csvfile:
			lector = csv.reader(csvfile, delimiter = ',', quotechar = '|')
			for pose in lector:
				tempPose = pose
			for i in range(6):
				verificador = float(tempPose[i]) == Target[i] and verificador
		return verificador

	def Compare(self, position):
		"""Compara el último estado del robot con el archivo CSV para evitar sobreecribir datos"""
		actualPose = []
		with open(self.path, newline = '') as csvfile:
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

	def Write(self, values):
		with open(self.path, 'a') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
			writer.writerow(values)