"""This module can construct SOAP request messages from a list of tag names. No netcode."""
#! /usr/bin/env python3

class SOAP_Constructor:
	def __init__(self, address):
		self.address = address
		
	# SOAP packet component creation methods
	def set_Action_Tag_Opener(self, action_Name, service_Name):
		"""This has a given xml structure as defined by the UPnP standard."""
		action_Tag_Opener = "<u:"
		action_Tag_Opener += action_Name
		action_Tag_Opener += " xmlns:s=\""
		action_Tag_Opener += service_Name
		action_Tag_Opener += "\">"
		self.action_Tag_Opener = action_Tag_Opener

	def set_Action_Tag_Closer(self, action_Name):
		"""This has a given xml structure as defined by the UPnP standard."""
		action_Tag_Closer = "</u:"
		action_Tag_Closer += action_Name
		action_Tag_Closer += ">"
		self.action_Tag_Closer = action_Tag_Closer

	def set_Arguments_Body_Spam(self, arguments_List):
		"""sfuzz is soon going to make this entirely defunct."""
		arguments_body = ""
		num_Arguments_Out = 0
		arguments_Out_List = []
		for entry in arguments_List:
			if entry.direction == "out":
				num_Arguments_Out += 1
				arguments_Out_List.append(entry.name)
				argument_Opener = "<" + entry.name + ">"
				argument_Closer = "</" + entry.name + ">"
			else:
				if "UINT" in entry.datatype.upper():
					user_Input = 99999999999
				else:
					user_Input = "-1"
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += str(user_Input)
				argument_Closer = "</" + entry.name + ">"
			arguments_body += argument_Opener
			arguments_body += argument_Closer
		self.arguments_body = arguments_body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def set_Arguments_Body(self, arguments_List):
		"""Takes user input to fill the fields of the variables you're submitting to
		the service."""
		arguments_body = ""
		num_Arguments_Out = 0
		arguments_Out_List	 = []
		for entry in arguments_List:
			if entry.direction == "out":
				num_Arguments_Out += 1
				arguments_Out_List.append(entry.name)
				argument_Opener = "<" + entry.name + ">"
				argument_Closer = "</" + entry.name + ">"
			else:
				user_Input = input("		Enter a value for %s: " % entry.name)
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += user_Input
				argument_Closer = "</" + entry.name + ">"
			arguments_body += argument_Opener
			arguments_body += argument_Closer
		self.arguments_body = arguments_body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def set_Control_URL(self, control_url):
		self.control_url = control_url

	def set_Control_Port(self, control_Port):
		self.control_Port = str(control_Port)

	def set_SOAP_Destination(self):
		destination = "http://"
		destination += str(self.address)
		destination += ":"
		destination += self.control_Port
		destination += self.control_url
		self.destination = destination

	# SOAP packet compilation methods
	def compile_SOAP_Message(self):
		"""Add the pieces of a SOAP packet together in sequence and call that a SOAP message."""
		SOAP_Message = ""
		SOAP_Message += self.soap_Envelope_Start
		SOAP_Message += self.action_Tag_Opener
		SOAP_Message += self.arguments_body
		SOAP_Message += self.action_Tag_Closer
		SOAP_Message += self.soap_Envelope_End
		self.SOAP_Message = SOAP_Message

	def prepare_clean_soap(self, device, this_action, this_Service):
		self.set_Action_Tag_Opener(this_action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_action.name)
		self.set_Arguments_Body(this_action.arguments)
		self.set_Control_URL(this_Service.control_url)
		self.set_Control_Port(device.presentation_port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	def prepare_Dirty_SOAP(self, device, this_action, this_Service):
		self.set_Action_Tag_Opener(this_action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_action.name)
		self.set_Arguments_Body(this_action.arguments)
		self.set_Control_URL(this_Service.control_url)
		self.set_Control_Port(device.presentation_port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	def prepare_auto_soap(self, device, this_action, this_Service):
		self.set_Action_Tag_Opener(this_action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_action.name)
		self.set_Arguments_Body_Spam(this_action.arguments)
		self.set_Control_URL(this_Service.control_url)
		self.set_Control_Port(device.presentation_port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()
