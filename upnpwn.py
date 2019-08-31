#!/usr/bin/env python 37
__author__ = "Jordan Sharp"
__copyright__ = "Copyright 2018"
__credits__ = ["Jordan Sharp"]
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "Jordan Sharp"
__email__ = "0xsee4@gmail.com"
__status__ = "Alpha"
__doc__ = "UPnPwn is a client for manually interacting with UPnP servers and clients. It supports SSDP, SCPD XML fetching, SOAP requests and (untested) GENA Eventing."

from ssdp_Discover import *
from scpd_Handler import *
from SOAP_Handler import *
from dirtySOAP import *
from UPnP_Attack_Dispatcher import *
from requests.auth import HTTPDigestAuth
import re
import pyfiglet
import urllib2
import xml.etree.ElementTree as ET

title_String = "		####### UPnPwn %s #######" % __version__

block = "\n\n\n\n\n\n\n"

main_Menu_String = """		Q | q | exit = Exit the program
		S | s = Scan for SSDP-responding hosts and list them
		H | h = Specify a host whose devices you want to explore\n"""

host_Menu_String = """
		D | d = Specify a device on this host whose services you want to explore
		M | m = Return to the main menu\n"""

service_Menu_String = """
		L | l = List all actions defined by this service (already listed above, but this clears duplicates)
		A | a = Specify an action to explore 
		R | r = Return to the device menu\n"""

device_Menu_Before_SCPD_String = """
		The following service list was obtained from SSDP packets. This list may contain 
		devices (lines beginning with 'uuid') alongside services. The interesting details of
		UPnP services (such as action names, arguments etc) are obtained from SCPD files.
		These have not yet been fetched, so we know very little right now.\n"""

device_Menu_Options = """		L | l = List SSDP-discovered services (already listed above)
		F | f = Fetch and parse all SCPD documents
		R | r = Return to the Host menu\n"""

device_Menu_After_SCPD_String = """
		H | h = Hail-Mary Test - Send '$(poweroff)' to every action (loud/fun)  
		L | l = List Services (already listed above)
		S | s = Specify a service to interact with
		R | r = Return to the Host menu\n"""

action_Menu_String = """
		A | a = List arguments of this action
		H | h = Hail-Mary Test - Send '$(poweroff)' to every action (loud/fun)
		S | s = List state variables for this action
		C | c = Send SOAP commands to execute this action (fun)
		R | r = Return to the Service menu\n"""

def inputHandler(prompt):
	prompt = "\n" + prompt
	userSelection = raw_input(prompt)
	userSelection = userSelection.upper()
	if "Q" in userSelection or "EXIT" in userSelection:
		print "Exiting UPnPwn."
		exit()
	return userSelection

def explore_Action(device, this_Service, action_Name):
	print block
	this_Action = this_Service.get_Action_By_Name(action_Name)
	action_Menu_Header = "\n\n		##### Action Menu for %s in %s on %s on %s at %s #####" % (this_Action.name, this_Service.name, device.device_InfoBundle.deviceType, device.device_InfoBundle.modelName, device.address)
	print action_Menu_Header
	print "		Which is an action of: 	", this_Service.name
	print "		Living on host: 		", device.address
	print "		Arguments:			", this_Action.num_Arguments
	print "		State Variables:		", this_Action.num_State_Variables
	this_Action.print_Action_Arguments()
	print "\n", action_Menu_String
	userSelection = ""
	while "Q" not in userSelection:
		userSelection = inputHandler("	Action: %s		Service: %s		On: %s@%s > " % (this_Action.name, this_Service.name, device.device_InfoBundle.deviceType, device.address))
		if type(userSelection) != "String":
			pass
		if "A" in userSelection:
			if len(this_Action.arguments) < 1:
				print "		This action takes no arguments. As an action, it takes itself a bit seriously..."
			else:
				this_Action.print_Action_Arguments()
			print action_Menu_String
		elif "S" in userSelection:
			if len(this_Action.state_Variable_Table.variables) == 0:
				print "		(!) No state variables are listed for this action."
			else:
				this_Action.state_Variable_Table.print_State_Variables()
		elif "C" in userSelection:
			userSelection = inputHandler("		Save SOAP packet? y/n > ")
			if "Y" in userSelection:
				dontDropIt = SOAP_Handler(device.address)
				dontDropIt.handle_Some_SOAP(device, this_Action, this_Service, "Clean")
				dontDropIt.save_SOAP_Message(device, this_Action, this_Service)
			else:
				dontDropIt = SOAP_Handler(device.address)
				dontDropIt.handle_Some_SOAP(device, this_Action, this_Service, "Clean")
				#dontDropIt.handle_Clean_SOAP(device, this_Action, this_Service)
		elif "R" in userSelection:
			return 0
		elif "H" in userSelection:
			atk = UPnP_Attack_Dispatcher(device)
			atk.hail_Mary_Simple_Test()

def explore_Service(device, service_ID):
	print block
	this_Service = device.service_List[service_ID]
	this_Service.name = this_Service.name.strip()
	userSelection = ""
	displayed_Action_Names = []
	for entry in this_Service.actions:
		displayed_Action_Names.append(entry.name)
	service_Menu_Header =  "\n\n		####### Service Menu for %s on %s on %s at %s #######" % (this_Service.name, device.device_InfoBundle.deviceType, device.device_InfoBundle.modelName, device.address)
	print service_Menu_Header
	this_Service.print_Service_Details()
	this_Service.print_Service_Actions()
	this_Service.populate_Argument_Datatypes()
	print service_Menu_String
	while "Q" not in userSelection:
		userSelection = inputHandler("		Service: %s	  On: %s@%s > " % (this_Service.name, device.device_InfoBundle.deviceType, device.address))
		if type(userSelection) != 'str':
			pass
		if "H" in userSelection:
			return 0
		elif "M" in userSelection:
			main_Menu()
		elif "L" in userSelection:
			this_Service.print_Service_Actions()
			print service_Menu_String
		elif "A" in userSelection:
			if re.search('\d+', userSelection):
				choiceList = re.findall(r'\d+', userSelection)
				choice = int(choiceList[0])
				explore_Action(device, this_Service, displayed_Action_Names[choice -1])
				print service_Menu_Header
				this_Service.print_Service_Details()
				this_Service.print_Service_Actions()
				print service_Menu_String
			else:
				userSelectionInt = int(raw_input("		Enter action ID > "))
				explore_Action(device, this_Service, displayed_Action_Names[userSelectionInt - 1])
				print service_Menu_Header
				this_Service.print_Service_Details()
				this_Service.print_Service_Actions()
				print service_Menu_String
		elif "R" in userSelection:
			return 0

def explore_Device(device):
	print block
	userSelection = ""
	scpd_Has_Been_Fetched = device.scpd_Has_Been_Fetched
	while "Q" not in userSelection:
		if scpd_Has_Been_Fetched == True:
			print block
			print "		##### Device Menu for %s on %s at %s #####" % (device.device_InfoBundle.deviceType, device.device_InfoBundle.modelName, device.address)
			device.device_InfoBundle.print_InfoBundle()
			device.remove_Empty_Services()
			device.gather_Device_Statistics()
			device.print_Device_Statistics()
			device.print_Device_Service_List()
			print device_Menu_After_SCPD_String
			userSelection = inputHandler("		%s@%s > " % (device.device_InfoBundle.deviceType, device.address))
			if type(userSelection) != 'str':
				pass
			if "L" in userSelection:
				device.print_Device_Service_List()
			elif "S" in userSelection:
				if device.num_Services == 1:
					print "		Only 1 service detected, automatically selecting that one."
					explore_Service(device, 0)
					print device_Menu_After_SCPD_String
				else:
					if re.search('\d+', userSelection):
						choiceList = re.findall(r'\d+', userSelection)
						choice = int(choiceList[0])
						explore_Service(device, choice -1)
					else:
						userSelectionInt = int(raw_input("		Enter Service ID > "))
						explore_Service(device, userSelectionInt - 1)
						print device_Menu_After_SCPD_String
			elif "R" in userSelection:
				return 0
			elif "H" in userSelection:
				hail_Mary_Simple_Flood(device)
		else:
			print "		####### Device Menu for Device-%s at %s #######" % (device.host_Index + 1, device.address)
			print device_Menu_Before_SCPD_String
			device.print_Device_SSDP_Service_List()
			print device_Menu_Options
			userSelection = inputHandler("		Device-%s@%s > " % (device.host_Index +1, device.address))
			if "F" in userSelection:
				device.scpd_Has_Been_Fetched = True
				device = read_SCPD_Root(device)
				print "		Fetched and parsed all SCPD documents!"
				scpd_Has_Been_Fetched = True
			elif "L" in userSelection:
				device.print_Device_SSDP_Service_List()
			elif "R" in userSelection:
				return 0

def explore_Host(host):
	print block
	userSelection = ""
	print "\n\n		####### Host Menu for %s #######" % host.address
	host.print_UPnP_Device_List()
	print host_Menu_String
	while "Q" not in userSelection:
		userSelection = inputHandler("		%s > " % host.address)
		if type(userSelection) != 'str':
			pass
		if "D" in userSelection:
			if host.num_UPnP_Devices == 1:
				print "		Only 1 device detected, automatically selecting that one."
				device = host.UPnP_Devices_List[0]
				explore_Device(device)
			else:
				userSelectionInt = int(raw_input("		Enter device index > "))
				device = host.UPnP_Devices_List[userSelectionInt -1]
				explore_Device(device)
		elif "M" in userSelection:
			return 0

def list_Hosts(this_Network):
	print block
	x = 1
	for host in this_Network.hosts_List:
		print "		+++++ Host ", x, " +++++"
		host.print_Basic_Host_Info()
		print ""
		for device in host.UPnP_Devices_List:
			device.print_Basic_Device_Info()
		print  "		+++++++++++++++++++\n"
		x += 1


# - Instantiates a Network Impression.
# - Iterates a query on a string for the presence of commands. Each command is one letter.
# Does not allow multiple options, the first detected is selected. Capitalises to allow input
# of either case.  

def main_Menu():
	this_Network = UPnP_Network_Impression(0)
	userSelection = ""
	while "Q" not in userSelection:
		userSelection = inputHandler("		UPnPwn > ")
		if type(userSelection) != 'str':
			pass
		if "S" in userSelection:
			this_Network = SSDP_Discover(this_Network)
			list_Hosts(this_Network)
			print main_Menu_String
		elif "H" in userSelection:
			if this_Network.num_Hosts == 1:
				print "		Only 1 host detected, automatically selecting that one."
				explore_Host(this_Network.hosts_List[0])
			else:
				userSelection = int(raw_input("		Enter host ID > "))
				explore_Host(this_Network.hosts_List[userSelection - 1])

def main():
	print __doc__
	print __email__
	print __author__
	print "\n\n"
	print title_String
	print main_Menu_String
	main_Menu()

if __name__ == '__main__':
	main()