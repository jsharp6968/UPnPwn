#! /usr/bin/env python3

from UPnP_Service import *
from UPnP_Device_InfoBundle import *

# This class defines a UPnP device object, which lives inside a Host object,
# and contains a list of Service objects.

class UPnP_Device:
	def __init__(self, address, host_index):
		self.host_index = host_index
		self.address = address
		self.presentation_url = ""
		self.server_string = ""
		self.device_xml_schema_string = ""
		self.service_xml_schema_string = ""
		self.root_xml_location = ""
		self.spec_version = ""

		# Ints
		self.service_xml_schema_major_version = 0
		self.service_xml_schema_minor_version = 0
		self.device_xml_schema_major_version = 0
		self.device_xml_schema_minor_version = 0
		self.presentation_port = 0
		self.num_services = 0
		self.num_actions = 0
		self.num_state_variables = 0

		# Lists
		self.service_list = []
		self.device_SSDP_Services_List = []

		# Booleans
		self.scpd_has_been_fetched = False

		# Objects
		self.device_infoBundle = UPnP_Device_InfoBundle("")

	def parse_SSDP_Bundle(self, bundle):
		if "UPNP:ROOTDEVICE" not in bundle.ST.upper() and "UUID:" not in bundle.ST.upper():
			this_Service = UPnP_Service(bundle.ST)
			this_Service.usn = bundle.usn
			this_Service.description_url = bundle.Location
			this_Service.ST = bundle.ST
			this_Service.Server = bundle.Server
			if self.server_string == "":
				self.server_string = bundle.Server
			self.device_SSDP_Services_List.append(this_Service)

	# Service methods
	def add_Service(self, service):
		self.service_list.append(service)
		self.num_services += 1
		self.num_actions += service.num_actions
		self.num_state_variables += service.num_state_variables

	def purge_Service_Repetitions(self):
		self.services_Set = set()
		self.services_Set = self.service_list
		self.service_list = self.services_Set

	def remove_Empty_Services(self):
		for service in self.service_list:
			if service.num_actions < 1:
				self.service_list.remove(service)

	def refresh_Description_URLs(self):
		scpd_URL_Set = set()
		for service in self.service_list:
			scpd_URL_Set.add(service.description_url)
		self.scpd_URL_List = scpd_URL_Set

	# Gather statistics and refresh URLs for modelling overall state, and printouts.
	def gather_Device_Statistics(self):
		self.num_actions = 0
		self.num_services = 0
		self.num_state_variables = 0
		for entry in self.service_list:
			self.num_actions += entry.num_actions
			self.num_state_variables += entry.num_state_variables
		self.num_services = len(self.service_list)

	# Printing methods
	def print_Basic_Device_Info(self):
		print("		Device Index:	       ", (self.host_index + 1))
		print("		Server: 		%s" % self.server_string)
		print("		Root XML URL: 		%s" % self.root_xml_location)
		print("		Packets received: 	%s" % len(self.device_SSDP_Services_List))
		print("")

	def print_Device_Statistics(self):
		print("		Services: 		", self.num_services)
		print("		Actions: 		", self.num_actions)
		print("		State Variables: 	", self.num_state_variables)
		print("")

	def print_Device_SSDP_service_list(self):
		x = 0
		for this_Entry in self.device_SSDP_Services_List:
			print("		Service ID %s: %s" % (x, this_Entry.name))
			x += 1
		print("")

	def print_Device_service_list(self):
		x = 1
		for this_Service in self.service_list:
			this_Service.name = this_Service.name.replace("urn:schemas-upnp-org:service:", "")
			this_Service.name = this_Service.name.replace("urn:dslforum-org:service:", "")
			this_Service.name = this_Service.name.replace(":1", "")
			print("		Service ID %s: %s" % (x, this_Service.name))
			print("		Num. of Actions: 		", this_Service.num_actions)
			print("		Num. of State Variables: 	", this_Service.num_state_variables)
			print("")
			x+=1