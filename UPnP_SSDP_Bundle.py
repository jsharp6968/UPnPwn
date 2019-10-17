#! /usr/bin/env python3

class UPnP_SSDP_Bundle:
	def __init__(self, usn, ST, Location, Server):
		self.usn = usn 
		self.http_code = 0
		self.ST = ST
		self.Location = Location
		self.Server = Server
		self.service_id = ""