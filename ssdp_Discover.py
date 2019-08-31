#! /usr/bin/env python 37
import sys
import re
import time
import pyfiglet
from progress.bar import Bar
from socket import *
from sets import Set
from upnp_Device import UPnP_Device
from scpd_Handler import read_SCPD_Root
from upnp_Host import UPnP_Host
from UPnP_Network_Impression import *
from UPnP_Service import *
from UPnP_SSDP_Bundle import *

# Default SSDP:Discover packet contents
ssdp_Discovery_MSEARCH_Header = "M-SEARCH * HTTP/1.1\r\n"
ssdp_Discovery_MSEARCH_Host = "Host: 239.255.255.250:1900\r\n"
ssdp_Discovery_MSEARCH_MAN = "Man: \"ssdp:discover\"\r\n"
ssdp_Discovery_MSEARCH_MX = "MX: 3\r\n"
ssdp_Discovery_MSEARCH_ST = "ST: ssdp:all\r\n"
ssdp_Discovery_MSEARCH_User_Agent = "User-Agent: UPnPwn V0.3\r\n"
ssdp_Discovery_MSEARCH_Packet_Termination = "\r\n"
ssdp_Discovery_MSEARCH_Port = 1900
ssdp_Discovery_MSEARCH_IP = "239.255.255.250"
ssdp_Search_Duration = 4

ssdp_Devices_Addresses_List = []
ssdp_Devices_Services_List = []
ssdp_Devices_Root_Documents_Dictionary = {"" : []}
ssdp_Devices_And_Services_Dictionary = {"" : [[]]}
ssdp_Devices_Count = 0
ssdp_Hosts_Dictionary = {}
UPnP_Device_Dictionary = {"" : []}

def get_ssdp_Devices_Addresses_List():
	return ssdp_Devices_Addresses_List

def get_ssdp_Devices_Count():
	return ssdp_Devices_Count

def get_UPnP_Device_Dictionary():
	return UPnP_Device_Dictionary

def purge_SSDP_Devices():
	global ssdp_Devices_And_Services_Dictionary
	global ssdp_Devices_Addresses_List
	global ssdp_Devices_Count
	del ssdp_Devices_Addresses_List[:]
	ssdp_Devices_And_Services_Dictionary.clear()
	ssdp_Devices_And_Services_Dictionary = {"" : [[]]}
	ssdp_Devices_Count = 0

def compile_SSDP_Discovery_Packet_Message():
	message_Output = ""
	message_Output += ssdp_Discovery_MSEARCH_Header
	message_Output += ssdp_Discovery_MSEARCH_Host
	message_Output += ssdp_Discovery_MSEARCH_MAN
	message_Output += ssdp_Discovery_MSEARCH_MX
	message_Output += ssdp_Discovery_MSEARCH_ST
	message_Output += ssdp_Discovery_MSEARCH_User_Agent
	message_Output += ssdp_Discovery_MSEARCH_Packet_Termination
	return message_Output

def define_Unicast_IP(address):
	global ssdp_Discovery_MSEARCH_IP
	ssdp_Discovery_MSEARCH_IP = address

def list_SSDP_Devices():
	print "		The following %s UPnP servers are available: " % ssdp_Devices_Count
	for x in range(0, ssdp_Devices_Count):
		print "		### Address: %s " % ssdp_Devices_Addresses_List[x]
		for y in range(0, len(ssdp_Devices_And_Services_Dictionary[ssdp_Devices_Addresses_List[x]])):
			tempList = []
			tempList = ssdp_Devices_And_Services_Dictionary[ssdp_Devices_Addresses_List[x]]
			individual_Service_Attribute_List = tempList[y]
			if y == 0:
				print "		# UPnP server identifier: %s " % individual_Service_Attribute_List[3]
				print "		# Number of available services: %s " % len(tempList)

def list_Device_Services(ssdp_Device_Address):
	for y in range(0, len(ssdp_Devices_And_Services_Dictionary[ssdp_Device_Address])):
		tempList = []
		tempList = ssdp_Devices_And_Services_Dictionary[ssdp_Device_Address]
		individual_Service_Attribute_List = tempList[y]
		if y == 0:
			print "		# UPnP server identifier: %s #" % individual_Service_Attribute_List[3]
			print "		# Number of available services: %s #\n" % len(tempList)
		print "		Service %s: %s" % (y+1, individual_Service_Attribute_List[1])
		#print "Location: ", individual_Service_Attribute_List[0]
		#print "USN: ", individual_Service_Attribute_List[2], "\n"

def extract_Substring_From_Packet_String(data, start, end):
	data_Upper = data.upper()
	beginning_Index = data_Upper.find(start.upper()) + len(start)
	ending_Index = data_Upper.find(end.upper(), beginning_Index)
	this_String = data[beginning_Index : ending_Index]
	this_String = this_String.strip()
	return this_String

def extract_Location_String(data):
	ssdp_Service_Location = extract_Substring_From_Packet_String(data, "LOCATION:", "\r\n")
	return ssdp_Service_Location

def extract_ST_String(data):
	ssdp_Service_Type = extract_Substring_From_Packet_String(data, "ST:", "\r\n")
	return ssdp_Service_Type

def extract_USN_String(data):
	ssdp_Service_USN = extract_Substring_From_Packet_String(data, "USN:", "\r\n")
	return ssdp_Service_USN

def extract_Server_String(data):
	ssdp_Server_String = extract_Substring_From_Packet_String(data, "SERVER:", "\r\n")
	return ssdp_Server_String

def extract_HTTP_Code(data):
	http_Code = extract_Substring_From_Packet_String(data, "HTTP/1.1 ", "\r\n")
	return http_Code

def extract_SSDP_Bundle(data):
	http_Code = extract_HTTP_Code(data)
	if data.startswith("HTTP/1.1 200"):
		this_SSDP_Bundle_Location = extract_Location_String(data)
		this_SSDP_Bundle_ST = extract_ST_String(data)
		this_SSDP_Bundle_USN = extract_USN_String(data)
		this_SSDP_Bundle_Server = extract_Server_String(data)
		this_SSDP_Bundle = UPnP_SSDP_Bundle(this_SSDP_Bundle_USN, this_SSDP_Bundle_ST, this_SSDP_Bundle_Location, this_SSDP_Bundle_Server)
	elif data.startswith("HTTP/1.1 2"):
		print "		(!) Received a 2xx but not 200 HTTP code: ", http_Code
	else:
		print "(!) Received HTTP Error response."
		return 1
	return this_SSDP_Bundle

def found_New_Host(this_Network, this_SSDP_Bundle, address):
	this_Device = UPnP_Device(address, 0)
	this_Device.server_String = this_SSDP_Bundle.Server
	this_Device.parse_SSDP_Bundle(this_SSDP_Bundle)

	this_Host = UPnP_Host(address)
	this_Host.UPnP_Root_XML_Locations.insert(0, this_SSDP_Bundle.Location)
	this_Device.root_XML_Location = this_SSDP_Bundle.Location
	this_Host.add_UPnP_Device(this_Device)

	this_Network.add_Host(this_Host)
	return this_Network

def found_New_Device(this_Network, this_Host, this_SSDP_Bundle, address):
	this_Device = UPnP_Device(address, this_Host.num_UPnP_Devices)
	this_Device.server_String = this_SSDP_Bundle.Server
	this_Device.root_XML_Location = this_SSDP_Bundle.Location
	this_Device.parse_SSDP_Bundle(this_SSDP_Bundle)
	#print "		Found a new Device on: ", this_SSDP_Bundle.Location

	this_Host.UPnP_Root_XML_Locations.append(this_SSDP_Bundle.Location)
	this_Host.add_UPnP_Device(this_Device)

	this_Network.update_Host_By_ID(this_Host.ID, this_Host)
	return this_Network

def found_New_Service(this_Network, this_Host, this_SSDP_Bundle, x):
	this_Service = UPnP_Service(this_SSDP_Bundle.ST)
	this_Service.set_Description_URL(this_SSDP_Bundle.Location)
	this_Service.set_ST(this_SSDP_Bundle.ST)
	this_Device = this_Host.UPnP_Devices_List[x]
	this_Device.device_SSDP_Services_List.append(this_Service)
	this_Network.update_Host_By_ID(this_Host.ID, this_Host)
	return this_Network

def populate_Network_Impression(ssdp_Packets, this_Network):
	for packet in ssdp_Packets:
		address = packet[0]
		data = packet[1]
		this_SSDP_Bundle = extract_SSDP_Bundle(data)
		if "NOT FOUND" == this_Network.get_Host_By_Address(address):
			# Found a new host on the network
			this_Network = found_New_Host(this_Network, this_SSDP_Bundle, address)
		else:
			this_Host = this_Network.get_Host_By_Address(address)
			if this_SSDP_Bundle.Location not in this_Host.UPnP_Root_XML_Locations:
				# Found a new UPnP device on a known host
				this_Network = found_New_Device(this_Network, this_Host, this_SSDP_Bundle, address)
			else:
				# Found a new service on known UPnP device on known host
				for x in range(0, len(this_Host.UPnP_Root_XML_Locations)):
					location = this_Host.UPnP_Root_XML_Locations[x]
					if location.startswith(this_SSDP_Bundle.Location):
						this_Network = found_New_Service(this_Network, this_Host, this_SSDP_Bundle, x)
	return this_Network

def SSDP_Discover(this_Network):
	this_Network = UPnP_Network_Impression(-1)
	ssdp_Responses = []
	ssdp_Discovery_Socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	ssdp_Discovery_Socket.settimeout(ssdp_Search_Duration)
	message = compile_SSDP_Discovery_Packet_Message()

	ssdp_Discovery_Socket.sendto(message, (ssdp_Discovery_MSEARCH_IP, ssdp_Discovery_MSEARCH_Port))
	t_Search_End = time.time() + ssdp_Search_Duration
	while time.time() < t_Search_End:
		try:
			tempList = []
			data, addr = ssdp_Discovery_Socket.recvfrom(1500)
			#print data
			#print addr
			tempList.insert(0, addr[0])
			tempList.insert(1, data)
			ssdp_Responses.append(tempList)
			if addr[0] not in this_Network.address_List:
				this_Network.address_List.append(addr[0])
				this_Network.ports_List.append(addr[1])
		except timeout:
			print "		Done search phase. Hosts detected: ", len(this_Network.address_List), "\n"
	if len(this_Network.address_List) < 1:
		ascii_banner = pyfiglet.figlet_format("Nothing to Pwn")
		print ascii_banner
		return this_Network
	else:
		this_Network.ID = 0
		this_Network =  populate_Network_Impression(ssdp_Responses, this_Network)
		return this_Network