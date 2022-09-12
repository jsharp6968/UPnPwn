#! /usr/bin/env python3
from UPnP_State_Variable_Table import *

# UPnP Standard 1.0 Error Codes
# 401: Invalid Action. No action by that name at this service.
# 402: Invalid Args. Could be any of the following: not enough in args, no in arg by that name, one or
#	more in args are of the wrong data type. Additionally, the UPnP Certification
#	Test Tool Shall return the following warning message if there are too many in-args
# 403: Deprecated...
# 501: Action Failed. May be returned in current state of service prevents invoking that action.
# 600: Argument Value Invalid. 
# 601: Argument Value out of range. An argument value is less than the minimum or more than the maximum value of
#	the allowedValueRange, or is not in the allowedValueList.
# 602: Optional Action Not Implemented. The requested action is optional and is not implemented by the device.
# 603: Out Of Memory. The device does not have sufficient memory available to complete the action.
#	This may be a temporary condition; the control point may choose to retry the
#	unmodified request again later and it may succeed if memory is available.
# 604: Human Intervention Required. The device has encountered an error condition which it cannot resolve itself and
#	required human intervention such as a reset or power cycle. See the device display or documentation for further guidance.
# 605: String argument too long.
# 606: Action not authorised. The specified action requires authorisation the sender does not have.
# 607: Signature failure. The sender's signature failed to verify.
# 608: Signature missing. The action requested requires a digital signature and there was none provided.
# 609: Not encrypted. This action requires confidentiality but the action was not delivered encrypted.
# 610: Invalid sequence. The <sequence> provided was not valid.
# 611: Invalid controlURL. The controlURL within the <freshness> element does not match the controlURL of
# the action actually invoked (or the controlURL in the HTTP header).
# 612: No such session. The session key reference is to a non-existent session. This could be because the
# device has expired a session, in which case the control point needs to open a new
# one.
# 600-699: TBD. Common action errors. Defined by UPnP Forum Technical Committee.
# 700-799: TBD. Action-specific errors for standard actions. Defined by UPnP Forum working
# committee.
# 800-899: TBD. Action-specific errors for non-standard actions. Defined by UPnP vendor.

class UPnP_Action:
	def __init__(self, name):
		self.name = name
		self.arguments = set()
		self.state_variable_table= UPnP_State_Variable_Table(name)
		self.num_arguments = 0
		self.num_state_variables = 0
		self.ID = 0
		self.requires_Input = False
		self.http_codes = []

	def check_Requires_Input(self):
		for argument in self.arguments:
			if argument.direction.upper() == "IN":
				self.requires_Input = True

	def set_Arguments_List(self, arguments):
		self.arguments = arguments
		self.num_arguments = len(self.arguments)

	def add_Argument_To_List(self, argument):
		self.arguments.add(argument)
		self.num_arguments += 1

	def set_State_Variable_Table(self, state_variable_table):
		self.state_variable_table= state_variable_table
		self.num_state_variables = len(state_variable_table.variables)

	def add_To_State_Variable_Table(self, state_variable):
		self.state_variable_table.variables.add(state_variable)
		self.num_state_variables += 1

	def fill_Argument_Datatypes(self):
		self.num_state_variables = len(self.state_variable_table.variables)
		print("The svt contains:")
		for entry in self.state_variable_table.variables:
			print("Variable: ", variable.name)
		print("And that's it.")
		for entry in self.arguments:
			this_Argument = entry.related_state_variable
			print(this_Argument)
			for variable in self.state_variable_table.variables:
				print("Checking variable: ", variable.name, " against: ", this_Argument)
				if variable.name.upper().strip() == this_Argument.upper().strip():
					entry.datatype = variable.datatype

	def print_Action_Arguments(self):
		print("\n		Note: Arguments with a direction of 'in' will have to be supplied by you, 'out' arguments will be supplied to you.\n")
		for entry in self.arguments:
			print("		Argument name:			", entry.name)
			print("		Argument type:			", entry.datatype)
			print("		Argument direction:		", entry.direction)
			print("		Related State Variable:		", entry.related_state_variable.strip())
			print("")
		print("\n")
