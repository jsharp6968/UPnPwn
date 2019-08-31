#! /usr/bin/env python 37

import urllib2
import xml.etree.ElementTree as ET
from UPnP_Action import *
from UPnP_Service import *
from UPnP_State_Variable import *
from UPnP_State_Variable_Table import *
from UPnP_Action_Argument import *
from UPnP_Device_InfoBundle import *

def save_Local_SCPD_File(scpd_File_Name, scpd_File_Data):
	with open(scpd_File_Name, 'w') as file:
		file.write(scpd_File_Data)

def fetch_SCPD_File_Contents(URL):
	scpd_File_Data = ""
	try:
		scpd_File_Data = urllib2.urlopen(URL).read()
	except:
		scpd_File_Data = urllib2.urlopen(URL + ".xml").read()
		print "		Nope, it was " + URL + ".xml !"
	return scpd_File_Data

def store_SCPD_Info(address, device):
	device.device_SCPD_URL_List = device_SCPD_URL_List
	device.set_Device_Services_List(device_Services_List)
	device.device_Eventing_URL_List = device_Eventing_URL_List
	device.device_Control_URL_List = device_Control_URL_List
	device.device_Service_State_Variable_Table_List = device_Service_State_Variable_Table_List
	device.device_Service_Action_Arguments_List_List = device_Service_Action_Arguments_List_List
	device.presentation_Port = presentation_Port
	device.presentationURL = presentationURL
	device.device_Actions_Dictionary = device_Actions_Dictionary
	return device

def save_SCPD_Root(location):
	scpd_File_Data = fetch_SCPD_File_Contents(location)
	scpd_File_Name = ''.join(e for e in location if e.isalnum())
	save_Local_SCPD_File(scpd_File_Name, scpd_File_Data)
	parse_Root_SCPD_XML(scpd_File_Data)

def get_Presentation_URL(location):
	global presentationURL
	presentationURL = location[0: location.find(":", 6)]
	return presentationURL

def get_Presentation_Port(rootURL):
	rootURL = rootURL.strip()
	presentation_port = 0
	if rootURL.startswith("http"):
		port_Index = rootURL.find(":", 9)
		end_Port_Index = rootURL.find("/", port_Index)
		port_As_String = rootURL[port_Index + 1 : end_Port_Index]
		presentation_port = int(port_As_String)
		try:
			presentation_port = int(port_As_String)
			#print "		Presentation port: ",  presentation_port
		except:
			print "{!} No port found in root description URL. Assuming presentation_port is 80 (it probably isn't)"
			presentation_port = 80
		return presentation_port
	else:
		port_Index = rootURL.find(":")
		port_Index += 1
		end_Port_Index = rootURL.find("/", port_Index)
		port_As_String = rootURL[port_Index : end_Port_Index]
		try:
			presentation_port = int(port_As_String)
			#print "		Presentation port: ",  presentation_port
		except:
			print "{!} No port found in root description URL. Assuming presentation_port is 80 (it probably isn't)"
			presentation_port = 80
		return presentation_port

def read_SCPD_Root(device):
	location = device.root_XML_Location.strip()
	print "		Reading this device's root XML description document from: ", location
	device.presentation_URL = get_Presentation_URL(location)
	print "		Using presentation_URL: ", device.presentation_URL
	device.presentation_Port = get_Presentation_Port(location)
	print "		Using presentation port: ", device.presentation_Port
	scpd_File_Data = urllib2.urlopen(location).read()
	print "		Read URL successfully!"
	prompt = "		Save this root description document locally? Y/N > "
	prompt = "\n" + prompt
	userSelection = raw_input(prompt)
	if userSelection.upper() == "Y":
		scpd_File_Name = ''.join(e for e in location if e.isalnum())
		save_Local_SCPD_File(scpd_File_Name, scpd_File_Data)
	device = parse_Root_SCPD_XML(scpd_File_Data, device)
	device.purge_Service_Repetitions()
	device.remove_Empty_Services()
	print "		Parsed root XML..."
	print "		Stored SCPD info..."
	return device

	#print "		You may have encountered a machine running a direct pairing service... uTorrent does this."
# Current code works with upnp.org schema for UPnP device version 1.0: <root xmlns="urn:schemas-upnp-org:device-1-0">
# This has 8 levels from the root level. Testing device is a Huawei HG659b.
#
# l1 = <SpecVersion> and <Device> - which is an Internet Gateway Device (IGD)
# l2 = <ServiceList> and useful info of IGD (serial number, device friendly name, presentation URL etc) and <deviceList> for further devices
# l3 = <Service>s from within the IGD ServiceList and <device>s in the deviceList, such as "WANDevice" and "LANDevice"
# l4 = <ServiceList>s of those further devices, and one further <deviceList>, in this case a child-device of "WANDevice"
# l5 = <Sevice>s within the ServiceLists of those other devices, and the final <device> which is a "WANConnectionDevice", and its ServiceList
# l6 = All service URLs for Services within the above ServiceLists, <Service>s within the WANConnectionDevice ServiceList
# l7 = All service URLs for Services within WANConnectionDevice
#
# The above list is very difficult to follow/visualise without an actual xml document to browse. Obviously this layout varies from schema to
# schema. The device desciption xml file URLs, control URLs and eventing URLs all live one level below the <Service> level, so you grab all three 
# at once. Note that all are relative URLs, not absolute - they have to be appended to the presentation URL. In some cases
# the <presentationURL> on l2 does not include the :port suffix - it's just an IPV4 address. This port will have to be appended to all URLs for 
# them to work.

def update_A_Service(device, this_Service):
	x = 0
	for service in device.service_List:
		if service.ST.upper().strip() == this_Service.ST.upper().strip():
			#print "		Updating a service: ", this_Service.ST
			device.service_List[x] = this_Service
			break
		x += 1
	return device

def add_A_Service(device, this_Service):
	x = 0
	for service in device.device_SSDP_Services_List:
		if service.ST.upper().strip() == this_Service.ST.upper().strip():
			print "		Adding a service: ", this_Service.ST
			device.add_Service(this_Service)
			break
		x += 1
	return device

def check_Element_For_Services(element):
	this_Service = UPnP_Service("NULL")
	element_Tag_As_String = str(element.tag).upper()
	if element_Tag_As_String.endswith("SERVICE"):
		for l2 in element:
			print l2.text
			print l2.tag
			print 2
			if l2.tag.upper().endswith("SCPDURL"):
				print "We found a description document!"
				print l2.tag.upper()
				this_Service.description_URL = l2.text
			elif l2.tag.upper().endswith("CONTROLURL"):
				this_Service.control_URL = l2.text
			elif l2.tag.upper().endswith("EVENTSUBURL"):
				this_Service.eventing_URL = l2.text
			elif l2.tag.upper().endswith("SERVICEID"):
				this_Service.service_ID = l2.text
			elif l2.tag.upper().endswith("SERVICETYPE") or l2.tag.upper().endswith("ST"):
				this_Service.name = l2.text
				this_Service.ST = l2.text
	return this_Service

def check_Element_For_Device_SpecVersion(element):
	spec_Version_String = "NULL"
	element_Tag_As_String = str(element.tag).upper()
	if element_Tag_As_String.endswith("SPECVERSION"):
		if element[0].tag.upper() == "MAJOR":
			spec_Version_String += element[0].text
		if element[1].tag.upper() == "MINOR":
			spec_Version_String += element[1].text
	return spec_Version_String

def check_Element_For_Device_InfoBundle(element, this_Device_InfoBundle):
	element_Tag_As_String = str(element.tag).upper()
	filledFields = 0
	if element_Tag_As_String.endswith("DEVICE"):
		for subElement in element:
			if subElement.tag.upper().endswith("DEVICETYPE"):
				deviceType = subElement.text
				deviceType = deviceType.replace("urn:schemas-upnp-org:device:", "")
				deviceType = deviceType.replace("urn:dslforum-org:device:", "")
				deviceType = deviceType.replace(":1", "")
				this_Device_InfoBundle.deviceType = deviceType
				filledFields += 1
			if subElement.tag.upper().endswith("FRIENDLYNAME"):
				this_Device_InfoBundle.friendlyName = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MANUFACTURER"):
				this_Device_InfoBundle.manufacturer = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MANUFACTURERURL"):
				this_Device_InfoBundle.manufacturerURL = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MODELDESCRIPTION"):
				this_Device_InfoBundle.modelDescription = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MODELNAME"):
				this_Device_InfoBundle.modelName = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MODELNUMBER"):
				this_Device_InfoBundle.modelNumber = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("MODELURL"):
				this_Device_InfoBundle.modelURL = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("SERIALNUMBER"):
				this_Device_InfoBundle.serialNumber = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("UDN"):
				this_Device_InfoBundle.UDN = subElement.text
				filledFields += 1
			if subElement.tag.upper().endswith("UPC"):
				this_Device_InfoBundle.UPC = subElement.text
				filledFields += 1
	this_Device_InfoBundle.filledFields = filledFields
	return this_Device_InfoBundle

def parse_Root_SCPD_XML(scpd_File_Data, device):
	root = ET.fromstring(scpd_File_Data)
	for l1 in root:
		# specVerions and and least one root device live here
		specVersion = check_Element_For_Device_SpecVersion(l1)
		if specVersion != "NULL":
			device.specVersion = specVersion
		this_Device_InfoBundle = UPnP_Device_InfoBundle(device.root_XML_Location)
		this_Device_InfoBundle = check_Element_For_Device_InfoBundle(l1, this_Device_InfoBundle)
		if this_Device_InfoBundle.filledFields > 0:
			device.device_InfoBundle = this_Device_InfoBundle
		for l2 in l1:
			for l3 in l2:
				this_Service = check_Element_For_Services(l3)
				if this_Service.name != "NULL":
					device = add_A_Service(device, this_Service)
				for l4 in l3:
					this_Service = check_Element_For_Services(l4)
					if this_Service.name != "NULL":
						device = add_A_Service(device, this_Service)
					for l5 in l4:
						this_Service = check_Element_For_Services(l5)
						if this_Service.name != "NULL":
							device = add_A_Service(device, this_Service)
						for l6 in l5:
							this_Service = check_Element_For_Services(l6)
							if this_Service.name != "NULL":
								device = add_A_Service(device, this_Service)
							for l7 in l6:
								this_Service = check_Element_For_Services(l7)
								if this_Service.name != "NULL":
									device = add_A_Service(device, this_Service)
	print "		Set all root-XML-derived lists..."
	print "		The current device has the following number of Services: ", len(device.service_List)
	device.refresh_Description_URLs()
	print "		We are handling: ", len(device.scpd_URL_List), " description document(s)."
	device = fetch_Service_Description_Documents(device.scpd_URL_List, device)
	return device

# This code works with upnp.org schema for a UPnP service version 1.0: <scpd xmlns="urn:schemas-upnp-org:service-1-0">
# The root level is called <scpd>. This file has 5 levels beyond root.
#
# l1 = <specVersion>, the <actionList> for this service and <serviceStateTable> for the variables which make up this service's state
# l2 = Numerous <action>s in the actionList and numerous <StateVariable>s in the serviceStateTable. Note that none yet have names.
# l3 = The <name> for each action in the actionList, the <argumentList> for each action, and the <name> and <dataType> for each state variable
# l4 = The <argument>s in each argumentList
# l5 = The <name>, <direction> and <relatedStateVariable> of each argument in an action's argument list.
#
# Note that the <direction> element on l5 refers to whether you will be reading a value FROM the server or writing a new value TO the server.
# All arguments with "in" <direction> have to be given a value in your SOAP request (at least in theory). All those with an "out" <direction>
# are listed in the SOAP request but you can (and should) send no value, ie for action <GetPublicIPAddress>, with one argument <NewPublicIPAddress>
# that has a <direction> of "out", you would send a SOAP request containing the line: 
# <NewPublicIPAddress></NewPublicIPAddress>

# The <stateVariables> have a "sendEvents" attribute. Unsure what this means, either it means you can't subscribe to it through the eventing 
# URL or nobody has subscribed yet... In the latter case it's useful for checking if any UPnP-enabled devices are subscribing to events.
# A GENA handler is in development for UPnPwn 0.4.

def parse_SCPD_Description_Document(description_File_Contents, description_Full_URL, device):
	current_Service = UPnP_Service("NULL")
	for this_Service in device.service_List:
		if description_Full_URL.strip().endswith(this_Service.description_URL.strip()):
			current_Service = this_Service
			break
	print "		Currently parsing details for service: ", current_Service.name
	root = ET.fromstring(description_File_Contents)
	for l1 in root:
		this_Tag1 = l1.tag.upper()
		if this_Tag1.endswith("SERVICESTATETABLE"):
			print "		Found the service's state table."
			for l2 in l1:
				this_State_Variable_Table = current_Service.state_Variable_Table
				this_State_Variable = UPnP_State_Variable(l2[0].text.strip(), l2[1].text.strip(), l2.attrib)
				print "		Adding a state variable named", l2[0].text.strip(), "to current service, dataType: ", l2[1].text.strip()
				this_State_Variable_Table.add_State_Variable(this_State_Variable)
				current_Service.state_Variable_Table = this_State_Variable_Table
				current_Service.num_State_Variables = len(this_State_Variable_Table.variables)
				device = update_A_Service(device, current_Service)
				device.gather_Device_Statistics()
				print "		This service now has ", current_Service.num_State_Variables, " state variable(s) associated with it."
		for l2 in l1:
			this_Action = UPnP_Action(l2.text.strip())
			thisTag = str(l2.tag).upper()
			if thisTag.endswith("ACTION"):
				for l3 in l2:
					thisTag = str(l3.tag)
					thisTag = thisTag.upper()
					if thisTag.endswith("NAME"):
						if l2.tag.upper().endswith("ACTION"):
							this_Action.name = l3.text.strip()
				try:
					if l2[1].tag.upper().endswith("ARGUMENTLIST"):
						x = 0
						try:
							while l2[1][x].tag.upper().endswith("ARGUMENT"):
								this_Argument = UPnP_Action_Argument(l2[1][x][0].text.strip("New"))
								this_Argument.direction = l2[1][x][1].text.strip()
								this_Argument.related_State_Variable = l2[1][x][2].text.strip()
								this_Action.add_Argument_To_List(this_Argument)
								x += 1
						except:
							#print "Going to add an Action to a Service..."
							current_Service.add_Action(this_Action)
							#print "Successfully added Action ", this_Action.name, " to Service ", current_Service.name
							device = update_A_Service(device, current_Service)
							#print "Successfully updated this service!"
				except:
					print "		Exception handling an argument list..."
				device = update_A_Service(device, current_Service)
	print "		Parsed through a description document..."
	return device

def save_SCPD_Description_Document(description_Full_URL):
	description_Filename = ''.join(e for e in description_Full_URL if e.isalnum())
	description_File_Contents = fetch_SCPD_File_Contents(description_Full_URL)
	save_Local_SCPD_File(description_Filename, description_File_Contents)

def read_SCPD_Description_Document(description_Full_URL, device):
	print "		Fetching: ", description_Full_URL
	description_File_Contents = fetch_SCPD_File_Contents(description_Full_URL)
	print "		Fetched a description document..."
	device = parse_SCPD_Description_Document(description_File_Contents, description_Full_URL, device)
	return device

def fetch_Service_Description_Documents(description_Document_Relative_Paths_List, device):
	for description_Document_Relative_Path in description_Document_Relative_Paths_List:
		description_Full_URL = ""
		description_Full_URL = device.presentation_URL + ":" + str(device.presentation_Port) + "/" + description_Document_Relative_Path
		description_Full_URL = description_Full_URL.strip()
		print "		Trying this URL: ", description_Full_URL
		device = read_SCPD_Description_Document(description_Full_URL, device)
	return device