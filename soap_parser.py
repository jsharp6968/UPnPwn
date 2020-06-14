#! /usr/bin/env python3

import xml.etree.ElementTree as ET

class SOAP_Parser:
	def __init__(self):
		pass

	# Parsing methods
	def parse_SOAP_Response(self, reply_Text):
		if reply_Text == "":
			return 0
		reply_Text = str(reply_Text)
		reply_Element = ET.fromstring(reply_Text)
		SOAP_Responses = {"" : ""}
		for entry in self.arguments_Out_List:
			for l2 in reply_Element:
				for l3 in l2:
					pass
			this_Response_Start = reply_Text.find("New" + entry, 1)
			this_Response_Start += len(entry) + 4
			this_Response_End = reply_Text.find(entry, this_Response_Start + 3)
			if this_Response_End == -1:
				SOAP_Responses[entry] = "NULL"
				#print("      ", entry, ": ", "NULL")
			else:
				this_Response_End -= 5
				this_Response = reply_Text[this_Response_Start : this_Response_End]
				this_Response = this_Response.strip("></\n ")
				SOAP_Responses[entry] = str(this_Response)
				#print("      ", entry, ": ", this_Response)
		return SOAP_Responses