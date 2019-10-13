#! /usr/bin/env python3

# This class defines a UPnP device object, which lives inside a Host object,
# and contains a list of Service objects.

class UPnP_Host:
	def __init__(self, address):
		self.address = address
		self.num_UPnP_Devices = 0
		self.UPnP_Root_XML_Locations = []
		self.UPnP_Devices_List = []

	def add_UPnP_Device(self, device):
		self.UPnP_Devices_List.append(device)
		self.num_UPnP_Devices += 1

	def get_UPnP_Device_Count(self):
		self.num_UPnP_Devices = len(self.UPnP_Devices_List)

	def set_Presentation_URL(self, presentation_URL):
		self.presentation_URL = presentation_URL

	def print_UPnP_Device_List(self):
		print("		The following %s UPnP root devices live on %s:\n" % (self.num_UPnP_Devices, 
			self.address))
		for device in self.UPnP_Devices_List:
			device.print_Basic_Device_Info()

	def print_Basic_Host_Info(self):
		print("		Address: ", self.address)
		print("		Devices: ", self.num_UPnP_Devices)
