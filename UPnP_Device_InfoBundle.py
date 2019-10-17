"""UPnP implementations on IGDs (Internet Gateway Devices) typically have a list
of information something like the below that they will provide you in their root
xml document."""
#! /usr/bin/env python3

class UPnP_Device_InfoBundle:
	def __init__(self, sourceDocumentURL):
		self.sourceDocumentURL = sourceDocumentURL
		self.deviceType = ""
		self.friendlyName = ""
		self.manufacturer = ""
		self.manufacturerURL = ""
		self.modelDescription = ""
		self.model_name = ""
		self.modelNumber = ""
		self.modelURL = ""
		self.serialNumber = ""
		self.UDN = ""
		self.UPC = ""

		self.filledFields = 0

	def print_InfoBundle(self):
		"""Print everything, cli formatted."""
		print("		Root XML Document:	", self.sourceDocumentURL)
		print("		Device Type:		", self.deviceType)
		print("		Friendly Name:		", self.friendlyName)
		print("		Manufacturer:		", self.manufacturer)
		print("		Manufacturer URL:	", self.manufacturerURL)
		print("		Model Description:	", self.modelDescription)
		print("		Model Name:		", self.model_name)
		print("		Model Number:		", self.modelNumber)
		print("		Model URL:		", self.modelURL)
		print("		Serial Number:		", self.serialNumber)
		print("		UDN:			", self.UDN)
		print("		UPC:			", self.UPC)