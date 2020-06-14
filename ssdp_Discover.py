"""This module handles all the SSDP discovery functions of the UPnP standard."""
#! /usr/bin/env python3
from upnp_Device import UPnP_Device
from upnp_Host import UPnP_Host
from UPnP_Network_Impression import UPnPNetworkImpression
from UPnP_Service import UPnP_Service
from UPnPwn_Print_Manager import do_pyfiglet
from SSDP_Extractor import extract_SSDP_Bundle
from SSDP_Dispatcher import send_discovery_packet_store_responses

def found_new_host(this_network, this_ssdp_bundle, address):
    """Each host must have at least one device, so create that and parse responses.
    Create host object. Add the new root XML doc to the Host and Device. Add the
    device to the host. Add the host to the network."""
    this_device = UPnP_Device(address, 0)
    this_device.server_string = this_ssdp_bundle.Server
    this_device.parse_SSDP_Bundle(this_ssdp_bundle)

    this_host = UPnP_Host(address)
    this_host.config_ID = this_ssdp_bundle.config_ID
    this_host.boot_ID = this_ssdp_bundle.boot_ID
    this_host.UPnP_Root_XML_Locations.insert(0, this_ssdp_bundle.Location)
    this_device.root_xml_location = this_ssdp_bundle.Location
    this_host.add_UPnP_Device(this_device)

    this_network.add_host(this_host)
    print("        Found a new host: %s" % this_host.address)
    return this_network

def found_new_device(this_network, this_host, this_ssdp_bundle, address):
    """Initialise the Device object with the Host's LAN address. Give it an index
    within the host. Set the URL for the root SCPD doc. Then parse the responses.
    Add the new device's description document to the host's doc list. Then add
    the device. Update the host on the network."""
    this_device = UPnP_Device(address, this_host.num_UPnP_Devices)
    this_device.server_string = this_ssdp_bundle.Server
    this_device.root_xml_location = this_ssdp_bundle.Location
    this_device.parse_SSDP_Bundle(this_ssdp_bundle)

    this_host.UPnP_Root_XML_Locations.append(this_ssdp_bundle.Location)
    this_host.add_UPnP_Device(this_device)

    this_network.update_host_by_impression_id(this_host.impression_id, this_host)
    return this_network

def found_new_service(this_network, this_host, this_ssdp_bundle, index):
    """Initialise the Service object with the Service Title. Set SCPD URL and title.
    Get the appropriate device object, for storing this new service. Update the network."""
    this_service = UPnP_Service(this_ssdp_bundle.ST)
    this_service.set_Description_URL(this_ssdp_bundle.Location)
    this_service.set_ST(this_ssdp_bundle.ST)

    this_device = this_host.upnp_devices_list[index]
    this_device.device_SSDP_Services_List.append(this_service)

    this_network.update_host_by_impression_id(this_host.impression_id, this_host)
    return this_network

def populate_network_impression(ssdp_packets, this_network):
    """Parse through responses and populate the network with active hosts."""
    for packet in ssdp_packets:
        address = packet[0]
        data = packet[1]
        this_ssdp_bundle = extract_SSDP_Bundle(data)
        if this_network.get_host_by_address(address) == "NOT FOUND":
            # Found a new host on the network.
            this_network = found_new_host(this_network, this_ssdp_bundle, address)
        else:
            # Known host.
            this_host = this_network.get_host_by_address(address)
            if this_ssdp_bundle.Location not in this_host.UPnP_Root_XML_Locations:
                # Found a new UPnP device on a known host.
                this_network = found_new_device(this_network, this_host,
                                                this_ssdp_bundle, address)
            else:
                # Found a new service on known UPnP device on known host.
                for xml_location in range(0, len(this_host.UPnP_Root_XML_Locations)):
                    location = this_host.UPnP_Root_XML_Locations[xml_location]
                    if location.startswith(this_ssdp_bundle.Location):
                        this_network = found_new_service(this_network, this_host,
                                                         this_ssdp_bundle, xml_location)
    return this_network

def ssdp_discover(this_network):
    """Creates a Network Impression object with -1 ID to indicate it's blank.
    Perfoms an SSDP discovery session as defined in the UPnP standard; sends a broadcast UDP packet
    to port 1900. All responding hosts will send one packet for each root device, as well as one
    packet for each service hosted, via unicast traffic."""
    this_network = UPnPNetworkImpression(-1)
    ssdp_responses = []

    this_network = send_discovery_packet_store_responses(this_network)
    if not this_network.address_list:
        # Nothing to Pwn.
        do_pyfiglet("Nothing   to  Pwn")
    else:
        # Set the ID to a sane value and return the network.
        this_network.ID = 0
        this_network = populate_network_impression(this_network.ssdp_bundle, this_network)
    return this_network
