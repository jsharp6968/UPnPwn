#! /usr/bin/env python3

class UPnP_State_Variable:
	def __init__(self, name, datatype, is_Eventing):
		self.name = name
		self.datatype = datatype
		self.is_Eventing = is_Eventing
		if datatype.upper().strip() == "STRING":
			self.value = ""
		elif datatype.upper().strip() == "BOOLEAN":
			self.value = False
		elif datatype.upper().strip() == "UI2" or datatype.upper().strip() == "UI1" or datatype.upper().strip() == "UI4":
			self.value = 0

	def set_Value(self, value):
		self.value = value

	def set_Name(self, name):
		self.name = name

	def set_Datatype(self, datatype):
		self.datatype = datatype

	def set_Is_Eventing(self, is_Eventing):
		self.is_Eventing = is_Eventing

	def set_Is_Complete(self, is_Complete):
		self.is_Complete = is_Complete

	def check_Is_Complete(self):
		if self.datatype == "" or self.name == "" or self.is_Eventing == None:
			self.is_Complete = False
			return False
		else:
			return True