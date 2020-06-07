"""Extracts data from an SSDP_Bundle object using simple parsing using the delimiters of desired substrings."""
#! /usr/bin/env python3
from UPnP_SSDP_Bundle import UPnP_SSDP_Bundle

def extract_Substring_From_Packet_String(data, start, end):
	data = str(data)
	start = str(start)
	end = str(end)
	data_Upper = data.upper()
	beginning_Index = data_Upper.find(start.upper())
	beginning_Index = beginning_Index + len(start)
	ending_Index = data_Upper.find(end.upper(), beginning_Index)
	this_String = data[beginning_Index : ending_Index]
	this_String = this_String.strip()
	return this_String

def extract_Location_String(data):
	ssdp_Service_Location = extract_Substring_From_Packet_String(data, "LOCATION:", '\n')
	return ssdp_Service_Location

def extract_ST_String(data):
	ssdp_Service_Type = extract_Substring_From_Packet_String(data, "ST:", '\n')
	return ssdp_Service_Type

def extract_usn_String(data):
	ssdp_Service_usn = extract_Substring_From_Packet_String(data, "usn:", '\n')
	return ssdp_Service_usn

def extract_Server_String(data):
	ssdp_Server_String = extract_Substring_From_Packet_String(data, "SERVER:", '\n')
	#print(ssdp_Server_String)
	return ssdp_Server_String

def extract_HTTP_Code(data):
	http_Code = int(extract_Substring_From_Packet_String(data, "HTTP/1.1 ", ' '))
	return http_Code

def extract_SSDP_Bundle(data):
	"""Extract the main aspects of an SSDP packet and store the HTTP response code only
	if we got a 200."""
	http_Code = extract_HTTP_Code(data)
	data = str(data)
	this_SSDP_Bundle = UPnP_SSDP_Bundle('1','1','1','1')
	if http_Code == 200:
		this_SSDP_Bundle.http_code = http_Code
		this_SSDP_Bundle_Location = extract_Location_String(data)
		this_SSDP_Bundle_ST = extract_ST_String(data)
		this_SSDP_Bundle_usn = extract_usn_String(data)
		this_SSDP_Bundle_Server = extract_Server_String(data)
		this_SSDP_Bundle = UPnP_SSDP_Bundle(this_SSDP_Bundle_usn, this_SSDP_Bundle_ST, this_SSDP_Bundle_Location, this_SSDP_Bundle_Server)
	elif "HTTP/1.1 200" in data:
		print("Running debug code, should have seen the 200")
		this_SSDP_Bundle.http_code = http_Code
		this_SSDP_Bundle_Location = extract_Location_String(data)
		this_SSDP_Bundle_ST = extract_ST_String(data)
		this_SSDP_Bundle_usn = extract_usn_String(data)
		this_SSDP_Bundle_Server = extract_Server_String(data)
		this_SSDP_Bundle = UPnP_SSDP_Bundle(this_SSDP_Bundle_usn, this_SSDP_Bundle_ST, this_SSDP_Bundle_Location, this_SSDP_Bundle_Server)
	elif "HTTP/1.1 2" in data:
		print("		(!) Received a 2xx but not 200 HTTP code: ", http_Code)
	else:
		print("(!) Received HTTP Error response.")
		return 1
	return this_SSDP_Bundle