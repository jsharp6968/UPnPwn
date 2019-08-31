#! /usr/bin/env python 27
from UPnP_Service import *
from UPnP_Device_InfoBundle import *

# This class defines a UPnP device and contains all the methods and data fields relevant to same.

class UPnP_Device:
	def __init__(self, address, host_Index):
		self.host_Index = host_Index
		self.address = address
		self.presentationURL = ""
		self.server_String = ""
		self.device_XML_Schema_String = ""
		self.service_XML_Schema_String = ""
		self.root_XML_Location = ""
		self.specVersion = ""

		# Ints
		self.service_XML_Schema_Major_Version = 0
		self.service_XML_Schema_Minor_Version = 0
		self.device_XML_Schema_Major_Version = 0
		self.device_XML_Schema_Minor_Version = 0
		self.presentation_Port = 0
		self.num_Services = 0
		self.num_Actions = 0
		self.num_State_Variables = 0

		# Lists
		self.service_List = []
		self.device_SSDP_Services_List = []

		# Dictionaries
		self.device_Actions_Dictionary = {"" : []}
		self.device_SCPD_Dictionary = {"" : []}
		self.ssdp_Dictionary = {"": []}

		# Booleans
		self.scpd_Has_Been_Fetched = False

		# Objects
		self.device_InfoBundle = UPnP_Device_InfoBundle("")

	def parse_SSDP_Bundle(self, bundle):
		if "UPNP:ROOTDEVICE" not in bundle.ST.upper() and "UUID:" not in bundle.ST.upper():
			this_Service = UPnP_Service(bundle.ST)
			this_Service.USN = bundle.USN
			this_Service.description_URL = bundle.Location
			this_Service.ST = bundle.ST
			this_Service.Server = bundle.Server
			if self.server_String == "":
				self.server_String = bundle.Server
			self.device_SSDP_Services_List.append(this_Service)

	def add_Service(self, service):
		self.service_List.append(service)
		self.num_Services += 1
		self.num_Actions += service.num_Actions
		self.num_State_Variables += service.num_State_Variables

	def refresh_Description_URLs(self):
		scpd_URL_Set = set()
		for service in self.service_List:
			scpd_URL_Set.add(service.description_URL)
		self.scpd_URL_List = scpd_URL_Set

	def purge_Service_Repetitions(self):
		self.services_Set = set()
		self.services_Set = self.service_List
		self.service_List = self.services_Set

	def remove_Empty_Services(self):
		for service in self.service_List:
			if service.num_Actions < 1:
				self.service_List.remove(service)

	# Gather statistics
	def gather_Device_Statistics(self):
		self.num_Actions = 0
		self.num_Services = 0
		self.num_State_Variables = 0
		for entry in self.service_List:
			self.num_Actions += entry.num_Actions
			self.num_State_Variables += entry.num_State_Variables
		self.num_Services = len(self.service_List)

	# Printing methods
	def print_Basic_Device_Info(self):
		print "		Device Index: 		", (self.host_Index + 1)
		print "		Server: 		%s" % self.server_String
		print "		Root XML URL: 		%s" % self.root_XML_Location
		print "		Packets received: 	%s" % len(self.device_SSDP_Services_List)
		print ""

	def print_Device_Statistics(self):
		print "		Services: 		", self.num_Services
		print "		Actions: 		", self.num_Actions
		print "		State Variables: 	", self.num_State_Variables
		print ""

	def print_Device_SSDP_Service_List(self):
		x = 0
		for this_Entry in self.device_SSDP_Services_List:
			print "		Service ID %s: %s" % (x, this_Entry.name)
			x += 1
		print ""

	def print_Device_Service_List(self):
		x = 1
		for this_Service in self.service_List:
			this_Service.name = this_Service.name.replace("urn:schemas-upnp-org:service:", "")
			this_Service.name = this_Service.name.replace("urn:dslforum-org:service:", "")
			this_Service.name = this_Service.name.replace(":1", "")
			print "		Service ID %s: %s" % (x, this_Service.name)
			print "		Num. of Actions: 		", this_Service.num_Actions
			print "		Num. of State Variables: 	", this_Service.num_State_Variables
			print ""
			x+=1