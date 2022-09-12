#! /usr/bin/env python3

class UPnP_Action_Argument():
	def __init__(self, name):
		self.name = name
		self.datatype = ""
		self.direction = ""
		self.value = ""
		self.related_state_variable = ""
	
	def set_Datatype(self, datatype):
		self.datatype = datatype

	def set_Name(self, name):
		self.name = name

	def set_Direction(self, direction):
		self.direction = direction

	def set_Value(self, value):
		self.value = value

	def set_related_state_variable(self, related_state_variable):
		self.related_state_variable = related_state_variable