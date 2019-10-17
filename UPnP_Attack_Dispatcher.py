"""The idea is to isolate anything you could call an attack from the rest of the
utility code, in order to make it as flexible and modular as possible. I've dumped
a few choice functions in here but really"""
#! /usr/bin/env python3
from dirtySOAP import *
from SOAP_Handler import *

class UPnP_Attack_Dispatcher:
	def __init__(self, target_device):
		self.target_device = target_device
		self.target_device_Name = target_device.device_infoBundle.deviceType
		self.target_device_address = target_device.address

	def overflow_Check_Int(self, this_action, this_Service, this_Device):
		"""Attack int-based services by exceeding their max value."""
		dontDropIt = SOAP_Handler(self.target_device_address)
		for argument in this_action.arguments:
			if argument.datatype.upper().contains("UINT"):
				this_Input = 0
				while this_Input < 10000000:
					dontDropIt.prepare_SOAP(this_Device, this_action, this_Service)
					this_Input += 1

	def type_Error_Footprint(self, device, this_action, this_Service):
		"""Attempt to find errors in an implementation by submitting data of the wrong datatype to a service."""
		total = 0
		type_List = [ "int", "float", "char", "byte", "string", "bool",  "shellcode" ]
		for service in self.target_device.service_list:
			for action in service.actions:
				print("		Now testing ", action.name, " in service ", service.name.strip(), " .")
				action.http_codes = dontDropIt.handle_Some_SOAP(self.target_device, action, service, "Dirty")
				#if 200 in action.http_codes:
				dontDropIt.save_SOAP_Message(self.target_device, action, service)
				total += 1
		print("		Conducted ", total, " tests in total.")
		interactable_Count = 0
		h401_count = 0
		h500_count = 0
		for service in self.target_device.service_list:
			for action in service.actions:
				if 200 in action.http_codes:
					print("		Action: ", action.name, " in Service: ", service.name, " INTERACTABLE")
					interactable_Count += 1
				elif 401 in action.http_codes:
					h401_count += 1
				elif 500 in action.http_codes:
					h500_count += 1
				else:
					pass
					#print "		Action: ", action.name, " in Service: ", service.name, " NOT INTERACTABLE ############"
		print("		Total of ", interactable_Count, " actions interactable from ", total)
		print("		Got ", h401_count, " total HTTP 401 Errors and ", h500_count, " total HTTP 500 Errors.")

	def hail_Mary_Simple_Test(self):
		"""Makes use of a hardcoded response in the Dirty SOAP type. Sends shellcode/something hacky and lazy.
		Soon to be replaced with actual attack vectors, although with IoT you never know..."""
		dontDropIt = dirtySOAP_Handler(self.target_device_address)
		total = 0
		for service in self.target_device.service_list:
			for action in service.actions:
				print("		Now testing ", action.name, " in service ", service.name.strip(), " .")
				action.http_codes = dontDropIt.handle_Some_SOAP(self.target_device, action, service, "Dirty")
				#if 200 in action.http_codes:
				dontDropIt.save_SOAP_Message(self.target_device, action, service)
				total += 1
		print("		Conducted ", total, " tests in total.")
		interactable_Count = 0
		h401_count = 0
		h500_count = 0
		for service in self.target_device.service_list:
			for action in service.actions:
				if 200 in action.http_codes:
					print("		Action: ", action.name, " in Service: ", service.name, " INTERACTABLE")
					interactable_Count += 1
				elif 401 in action.http_codes:
					h401_count += 1
				elif 500 in action.http_codes:
					h500_count += 1
				else:
					pass
					#print "		Action: ", action.name, " in Service: ", service.name, " NOT INTERACTABLE ############"
		print("		Total of ", interactable_Count, " actions interactable from ", total)
		print("		Got ", h401_count, " total HTTP 401 Errors and ", h500_count, " total HTTP 500 Errors.")

	def send_Dirty_SOAP(self, this_action, this_Service):
		"""Same as the regular SOAP send function, but with setted HTTP response codes.
		Probably defunct now, but as the SOAP handling code is in flux I'll keep it for now."""
		these_Status_Codes = set()
		dirt = input("		Enter some dirt to send as an action argument > ")
		count = int(input("		Number of packets to send > "))
		while count > 0:
			some_Status_Codes = dirtySOAP.handle_Dirty_SOAP(self.target_device, this_action, this_Service, dirt)
			for status_Code in some_Status_Codes:
				these_Status_Codes.add(status_Code)
			count -= 1
		return these_Status_Codes