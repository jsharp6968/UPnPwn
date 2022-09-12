"""This module defines the UPnPNetworkImpression class."""
#! /usr/bin/env python3
import datetime
from upnp_Host import UPnP_Host

class UPnPNetworkImpression:
    """Stores a snapshot, or impression, of the LAN with respect to UPnP traffic. This is the core
    object of the program; all host, device, service and action objects live inside."""
    def __init__(self, impression_id):
        self.impression_id = impression_id
        self.timestamp = str(datetime.datetime.now())
        self.ssdp_bundle = []
        self.num_hosts = 0
        self.address_list = []
        self.ports_list = []
        self.hosts_list = []

    def add_host(self, host):
        """Add a host to the network."""
        host.impression_id = self.num_hosts
        self.hosts_list.append(host)
        self.address_list.append(host.address    )
        self.num_hosts += 1
        return "Added a host."

    def purge_host_by_impression_id(self, impression_id):
        """Remove a host from the network, one-shot."""
        for host in self.hosts_list:
            if impression_id == host.impression_id:
                self.hosts_list.remove(host)
                break
        return "Removed host."

    def get_host_by_impression_id(self, impression_id):
        """Retrieve a host by impression_id."""
        output_host = UPnP_Host(0)
        for host in self.hosts_list:
            if impression_id == host.impression_id:
                output_host = host
                break
        return output_host

    def update_host_by_impression_id(self, impression_id, host_incoming):
        """Update a host with given impression_id."""
        for host in self.hosts_list:
            if impression_id == host.impression_id:
                host = host_incoming
                return "Host updated."

    def get_host_by_address(self, address):
        """Retrieve a host with given LAN address."""
        for host in self.hosts_list:
            if address == host.address:
                return host
        return "NOT FOUND"
