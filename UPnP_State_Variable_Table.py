#! /usr/bin/env python3

class UPnP_State_Variable_Table:
	def __init__(self, name):
		self.variables = set()
		self.name = name
		self.num_variables = 0

	def add_State_Variable(self, state_variable):
		self.variables.add(state_variable)
		self.num_variables = len(self.variables)

	def print_State_Variables(self):
		print("")
		for variable in self.variables:
			print("		Name: 	", variable.name)
			print("		Datatype:	", variable.datatype)
			print("		Is eventing:	", variable.is_eventing)
			print("		Value:		", variable.value, "\n")
		print("")