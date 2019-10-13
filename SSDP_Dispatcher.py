"""Module for controlling """
#! /usr/bin/env python3
import time
from datetime import datetime
from socket import *

# Default SSDP:Discovery packet contents
ssdp_Discovery_MSEARCH_Header = "M-SEARCH * HTTP/1.1\r\n"
ssdp_Discovery_MSEARCH_Host = "Host: 239.255.255.250:1900\r\n"
ssdp_Discovery_MSEARCH_MAN = "Man: \"ssdp:discover\"\r\n"
ssdp_Discovery_MSEARCH_MX = "MX: 3\r\n"
ssdp_Discovery_MSEARCH_ST = "ST: ssdp:all\r\n"
ssdp_Discovery_MSEARCH_User_Agent = "User-Agent: UPnPwn V0.3\r\n"
ssdp_Discovery_MSEARCH_Packet_Termination = "\r\n"
ssdp_Discovery_MSEARCH_IP = "239.255.255.250"
ssdp_Discovery_MSEARCH_Port = 1900
ssdp_Search_Duration = 3

def compile_SSDP_Discovery_Packet_Message():
	message_Output = ""
	message_Output += ssdp_Discovery_MSEARCH_Header
	message_Output += ssdp_Discovery_MSEARCH_Host
	message_Output += ssdp_Discovery_MSEARCH_MAN
	message_Output += ssdp_Discovery_MSEARCH_MX
	message_Output += ssdp_Discovery_MSEARCH_ST
	message_Output += ssdp_Discovery_MSEARCH_User_Agent
	message_Output += ssdp_Discovery_MSEARCH_Packet_Termination
	return message_Output

def define_Unicast_IP(address):
	global ssdp_Discovery_MSEARCH_IP
	ssdp_Discovery_MSEARCH_IP = address

def send_discovery_packet_store_responses(this_Network):
	# Create socket for SSDP discovery networking. Compile message into string, then bytes.
	ssdp_Discovery_Socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	ssdp_Discovery_Socket.settimeout(ssdp_Search_Duration)
	message = compile_SSDP_Discovery_Packet_Message()
	b = bytes(message, 'utf-8')

	# Print some output. Send discovery packet and listen for search duration.
	print("	Sent SSDP discovery packet at ", datetime.now())
	t_Search_End = time.time() + ssdp_Search_Duration
	ssdp_Discovery_Socket.sendto(b, (ssdp_Discovery_MSEARCH_IP, ssdp_Discovery_MSEARCH_Port))
	ssdp_Responses = []
	while time.time() < t_Search_End:
		try:
			response = []
			data, addr = ssdp_Discovery_Socket.recvfrom(1500)
			response.insert(0, addr[0])
			response.insert(1, data)

			# Store a response for later processing. Add a new host to the Network Impression if detected.
			ssdp_Responses.append(response)
			if addr[0] not in this_Network.address_List:
				this_Network.address_List.append(addr[0])
				this_Network.ports_List.append(addr[1])
			print("		SSDP response packet received at ", datetime.datetime.now())

		except timeout:
			print("	Done search phase. Hosts detected: ", len(this_Network.address_List), "\n")
	this_Network.ssdp_bundle = ssdp_Responses
	return this_Network