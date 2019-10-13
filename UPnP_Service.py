#! /usr/bin/env python3
from UPnP_State_Variable_Table import *

class UPnP_Service:
	def __init__(self, name):
		self.name = name	
		self.interactions_Count = 0
		self.errors_Count = 0
		self.is_Vulnerable = False
		self.num_actions = 0
		self.num_state_variables = 0

		self.actions = set()
		self.state_variable_table= UPnP_State_Variable_Table(self.name)

		self.description_url = ""
		self.control_url = ""
		self.presentation_url = ""
		self.eventing_URL = ""

		self.usn = ""
		self.ST = name
		self.service_id = ""

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
		action.ID = self.num_actions
		self.actions.add(action)
		self.num_actions += 1
		self.num_state_variables += action.num_state_variables

	def update_Action(self, updated_action):
		for action in self.actions:
			if updated_action.name == action.name:
				action = updated_action
				break
	def populate_Argument_Datatypes(self):
		for action in self.actions:
			for argument in action.arguments:
				for state_variable in self.state_variable_table.variables:
					if argument.related_state_variable.strip() == state_variable.name.strip():
						action.add_To_State_Variable_Table(state_variable)
						argument.datatype = state_variable.datatype 
			#action.num_state_variables = len(action.state_variable_table.variables)

	def add_State_Variable_Table(self, state_variable_table):
		self.state_variable_table= state_variable_table

	def set_Description_URL(self, description_url):
		self.description_url = description_url

	def set_Control_URL(self, control_url):
		self.control_url = control_url

	def set_Presentation_URL(self, presentation_url):
		self.presentation_url = presentation_url

	def set_Eventing_URL(self, eventing_URL):
		self.eventing_URL = eventing_URL

	def set_usn(self, usn):
		self.usn = usn

	def set_ST(self, ST):
		self.ST = ST

	def print_Service_Actions(self):
		x = 1
		for entry in self.actions:
			print("		Action %s: 	%s" % (x, entry.name))
			#print "		Num. Arguments: ", entry.num_arguments
			#print "		Num. State Var: ", entry.num_state_variables
			#print ""
			x += 1

	def print_Service_Details(self):
		print("		Service Name: 	", self.name)
		print("		Desc. URL:	", self.description_url)
		print("		Control URL: 	", self.control_url)
		print("		Eventing URL: 	", self.eventing_URL)
		print("		Actions: 	", self.num_actions)
		print("		State Vars:	", self.num_state_variables)
		print("")