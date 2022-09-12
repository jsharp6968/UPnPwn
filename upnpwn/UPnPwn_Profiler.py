"""This module profiles devices, gathers statistics and is slightly malicious."""
#! /usr/bin/env python3
from termcolor import colored
from SOAP_Handler import SOAPHandler

class UPnPwn_Profiler:
	def __init__(self, target_device):
		self.device = target_device

	def print_All_State_Variables(self):
		for service in self.device.service_list:
			if service.num_actions > 0:
				service.state_variable_table.print_State_Variables()

	def profile_Null_Actions(self):
		total_Actions_Profiled = 0
		dont_drop_it = SOAPHandler(self.device.address)
		output_Profile = ""
		for service in self.device.service_list:
			if service.num_actions > 0:
				output_Profile += "        Service: " + service.name + "\n"
				for action in service.actions:
					action.check_Requires_Input()
					if action.requires_Input == True:
						print("        Now profiling " + action.name + " in service " + service.name + ".")
						dont_drop_it.handle_clean_soap(self.device, action, service, 0, 0, 1)
						total_Actions_Profiled += 1
				for variable in service.state_variable_table.variables:
					if variable.is_filled:
						output_Profile += "        " + variable.name + ": " + str(variable.value) + "\n"
				output_Profile += "\n"
		print(colored(output_Profile, "green"))
		print("        Conducted ", total_Actions_Profiled, " tests in total.")

	def profile_Mute_Actions(self):
		total_Actions_Profiled = 0
		total_Successes = 0
		dont_drop_it = SOAPHandler(self.device.address)
		output_Profile = ""
		for service in self.device.service_list:
			if service.num_actions > 0:
				output_Profile += "        >>> Service: " + service.name + "\n"
				for action in service.actions:
					action.check_Requires_Input()
					if action.requires_Input == False:
						print("        Now profiling " + action.name + " in service " + service.name + ".")
						dont_drop_it.handle_clean_soap(self.device, action, service, 0, 0, 0)
						total_Actions_Profiled += 1
				for variable in service.state_variable_table.variables:
					if variable.is_filled:
						output_Profile += "        " + variable.name + ": " + str(variable.value) + "\n"
						total_Successes += 1
				output_Profile += "\n"
		print(colored(output_Profile, "green"))
		print("        Conducted ", total_Actions_Profiled, " tests in total, " + str(total_Successes) + " state variables gathered.")

