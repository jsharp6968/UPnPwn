#! /usr/bin/env python 27
from UPnP_State_Variable_Table import *

class UPnP_Service:
	def __init__(self, name):
		self.name = name	
		self.interactions_Count = 0
		self.errors_Count = 0
		self.is_Vulnerable = False
		self.num_Actions = 0
		self.num_State_Variables = 0

		self.actions = set()
		self.state_Variable_Table = UPnP_State_Variable_Table(self.name)

		self.description_URL = ""
		self.control_URL = ""
		self.presentation_URL = ""
		self.eventing_URL = ""

		self.USN = ""
		self.ST = name
		self.service_ID = ""

	def get_Action_By_ID(self, ID):
		for action in self.actions:
			if action.ID == ID:
				return action

	def get_Action_By_Name(self, name):
		for action in self.actions:
			if action.name == name:
				return action

	def add_Actions_List(self, actions):
		for action in actions:
			self.actions.add(action)

	def add_Action(self, action):
		action.ID = self.num_Actions
		self.actions.add(action)
		self.num_Actions += 1
		self.num_State_Variables += action.num_State_Variables

	def update_Action(self, updated_Action):
		for action in self.actions:
			if updated_Action.name == action.name:
				action = updated_Action
				break
	def populate_Argument_Datatypes(self):
		for action in self.actions:
			for argument in action.arguments:
				for state_Variable in self.state_Variable_Table.variables:
					if argument.related_State_Variable.strip() == state_Variable.name.strip():
						action.add_To_State_Variable_Table(state_Variable)
						argument.datatype = state_Variable.datatype 
			#action.num_State_Variables = len(action.state_Variable_Table.variables)

	def add_State_Variable_Table(self, state_Variable_Table):
		self.state_Variable_Table = state_Variable_Table

	def set_Description_URL(self, description_URL):
		self.description_URL = description_URL

	def set_Control_URL(self, control_URL):
		self.control_URL = control_URL

	def set_Presentation_URL(self, presentation_URL):
		self.presentation_URL = presentation_URL

	def set_Eventing_URL(self, eventing_URL):
		self.eventing_URL = eventing_URL

	def set_USN(self, USN):
		self.USN = USN

	def set_ST(self, ST):
		self.ST = ST

	def print_Service_Actions(self):
		x = 1
		for entry in self.actions:
			print "		Action %s: 	%s" % (x, entry.name)
			#print "		Num. Arguments: ", entry.num_Arguments
			#print "		Num. State Var: ", entry.num_State_Variables
			#print ""
			x += 1

	def print_Service_Details(self):
		print "		Service Name: 	", self.name
		print "		Desc. URL:	", self.description_URL
		print "		Control URL: 	", self.control_URL
		print "		Eventing URL: 	", self.eventing_URL
		print "		Actions: 	", self.num_Actions
		print "		State Vars:	", self.num_State_Variables
		print ""