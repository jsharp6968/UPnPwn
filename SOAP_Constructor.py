#! /usr/bin/env python3

class SOAP_Constructor(SOAP_Handler):
	def __init__(self):
		pass
		
	# SOAP packet component creation methods
	def set_Action_Tag_Opener(self, action_Name, service_Name):
		action_Tag_Opener = "<u:"
		action_Tag_Opener += action_Name
		action_Tag_Opener += " xmlns:s=\""
		action_Tag_Opener += service_Name
		action_Tag_Opener += "\">"
		self.action_Tag_Opener = action_Tag_Opener

	def set_Action_Tag_Closer(self, action_Name):
		action_Tag_Closer = "</u:"
		action_Tag_Closer += action_Name
		action_Tag_Closer += ">"
		self.action_Tag_Closer = action_Tag_Closer

	def set_Arguments_Body_Spam(self, arguments_List):
		arguments_Body = ""
		num_Arguments_Out = 0
		arguments_Out_List = []
		for entry in arguments_List:
			if entry.direction == "out":
				num_Arguments_Out += 1
				arguments_Out_List.append(entry.name)
				argument_Opener = "<" + entry.name + ">"
				argument_Closer = "</" + entry.name + ">"
			else:
				#user_Input = raw_input("		Enter a value for %s: " % entry.name)
				if "UINT" in entry.datatype.upper():
					user_Input = 99999999999
				else:
					user_Input = "-1"
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += user_Input
				argument_Closer = "</" + entry.name + ">"
			arguments_Body += argument_Opener
			arguments_Body += argument_Closer
		self.arguments_Body = arguments_Body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def set_Arguments_Body(self, arguments_List):
		arguments_Body = ""
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
			arguments_Body += argument_Opener
			arguments_Body += argument_Closer
		self.arguments_Body = arguments_Body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def set_Control_URL(self, control_URL):
		self.control_URL = control_URL

	def set_Control_Port(self, control_Port):
		self.control_Port = str(control_Port)
		#self.control_Port = str(37443)

	def set_SOAP_Destination(self):
		destination = "http://"
		destination += str(self.address_String)
		destination += ":"
		destination += self.control_Port
		destination += self.control_URL
		self.destination = destination

	# SOAP packet compilation methods
	def compile_SOAP_Message(self):
		SOAP_Message = ""
		SOAP_Message += self.soap_Envelope_Start
		SOAP_Message += self.action_Tag_Opener
		SOAP_Message += self.arguments_Body
		SOAP_Message += self.action_Tag_Closer
		SOAP_Message += self.soap_Envelope_End
		self.SOAP_Message = SOAP_Message

	def prepare_clean_soap(self, device, this_Action, this_Service):
		self.set_Action_Tag_Opener(this_Action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_Action.name)
		self.set_Arguments_Body(this_Action.arguments)
		self.set_Control_URL(this_Service.control_URL)
		self.set_Control_Port(device.presentation_Port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	def prepare_Dirty_SOAP(self, device, this_Action, this_Service):
		self.set_Action_Tag_Opener(this_Action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_Action.name)
		self.set_Arguments_Body(this_Action.arguments)
		self.set_Control_URL(this_Service.control_URL)
		self.set_Control_Port(device.presentation_Port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	def prepare_auto_soap(self, device, this_Action, this_Service):
		self.set_Action_Tag_Opener(this_Action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_Action.name)
		self.set_Arguments_Body_Spam(this_Action.arguments)
		self.set_Control_URL(this_Service.control_URL)
		self.set_Control_Port(device.presentation_Port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	"""
	type_list = ["int", "float", "char", "byte", "string", "bool", "shellcode"]
	for x in range(0, len(type_list)):
                this_type = type_list[x]
                if this_type == "int":
                    this_type = "8"
                elif this_type == "float":
                    this_type = "2.349745"
                elif this_type == "char":
                    this_type = 'c'
                elif this_type == "byte":
                    this_type = "\xdb"
                elif this_type == "string":
                    this_type == "UPnPwn"
                elif this_type == "bool":
                    this_type == "1"
                elif this_type == "shellcode":
                    this_type == """#\x31\xc0\x50\x68\x62\x6f\x6f\x74\x68\x6e\x2f\x72\x65\x68\x2f
                   # \x73\x62\x69\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"""
