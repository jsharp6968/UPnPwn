#! /usr/bin/env python 37

class UPnP_SSDP_Bundle:
	def __init__(self, USN, ST, Location, Server):
		self.USN = USN 
		self.ST = ST
		self.Location = Location
		self.Server = Server
		self.service_ID = ""