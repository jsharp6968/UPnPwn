#! /usr/bin/env python 37

import datetime

class UPnP_Network_Impression:
	def __init__(self, ID):
		self.ID = ID
		self.timestamp = str(datetime.datetime.now())
		self.num_Hosts = 0
		self.address_List = []
		self.ports_List = []
		self.hosts_List = []

	def add_Host(self, host):
		host.ID = self.num_Hosts
		self.hosts_List.append(host)
		self.num_Hosts += 1

	def purge_Host_By_ID(self, ID):
		for host in self.hosts_List:
			if ID == host.ID:
				self.hosts_List.remove(host)

	def get_Host_By_ID(self, ID):
		for host in self.hosts_List:
			if ID == host.ID:
				return host

	def update_Host_By_ID(self, ID, host_Incoming):
		for host in self.hosts_List:
			if ID == host.ID:
				host = host_Incoming

	def get_Host_By_Address(self, address):
		for host in self.hosts_List:
			if address == host.address:
				return host
		return "NOT FOUND"