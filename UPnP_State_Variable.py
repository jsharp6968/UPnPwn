#! /usr/bin/env python3

class UPnP_State_Variable:
	def __init__(self, name, datatype, is_eventing):
		self.name = name
		self.datatype = datatype
		self.is_eventing = is_eventing
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

	def set_Is_Eventing(self, is_eventing):
		self.is_eventing = is_eventing

	def set_Is_Complete(self, is_complete):
		self.is_complete = is_complete

	def check_Is_Complete(self):
		if self.datatype == "" or self.name == "" or self.is_eventing == None:
			self.is_complete = False
			return False
		else:
			return True