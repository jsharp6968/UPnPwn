#! /usr/bin/env python3

# This class defines a UPnP device object, which lives inside a Host object,
# and contains a list of Service objects.

class UPnP_Host:
	def __init__(self, address):
		self.address = address
		self.num_UPnP_Devices = 0
		self.UPnP_Root_XML_Locations = []
		self.upnp_devices_list = []
		self.config_ID = 0
		self.boot_ID = 0

	def add_UPnP_Device(self, device):
		self.upnp_devices_list.append(device)
		self.num_UPnP_Devices += 1

	def get_UPnP_Device_Count(self):
		self.num_UPnP_Devices = len(self.upnp_devices_list)

	def set_Presentation_URL(self, presentation_url):
		self.presentation_url = presentation_url

	def print_UPnP_Device_List(self):
		print("        The following %s UPnP root devices live on %s:\n" % (self.num_UPnP_Devices, 
			self.address))
		for device in self.upnp_devices_list:
			device.print_Basic_Device_Info()

	def print_Basic_Host_Info(self):
		print("        Address: " + self.address)
		print("        Devices: " + str(self.num_UPnP_Devices))
		print("        Config ID: " + str(self.config_ID))
		print("        Boot ID: " + str(self.boot_ID))
