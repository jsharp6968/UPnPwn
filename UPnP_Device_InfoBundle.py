#! /usr/bin/env python 37

class UPnP_Device_InfoBundle:
	def __init__(self, sourceDocumentURL):
		self.sourceDocumentURL = sourceDocumentURL
		self.deviceType = ""
		self.friendlyName = ""
		self.manufacturer = ""
		self.manufacturerURL = ""
		self.modelDescription = ""
		self.modelName = ""
		self.modelNumber = ""
		self.modelURL = ""
		self.serialNumber = ""
		self.UDN = ""
		self.UPC = ""

		self.filledFields = 0

	def print_InfoBundle(self):
		print "		Root XML Document:	", self.sourceDocumentURL
		print "		Device Type:		", self.deviceType
		print "		Friendly Name:		", self.friendlyName
		print "		Manufacturer:		", self.manufacturer
		print "		Manufacturer URL:	", self.manufacturerURL
		print "		Model Description:	", self.modelDescription
		print "		Model Name:		", self.modelName
		print "		Model Number:		", self.modelNumber
		print "		Model URL:		", self.modelURL
		print "		Serial Number:		", self.serialNumber
		print "		UDN:			", self.UDN
		print "		UPC:			", self.UPC