#! /usr/bin/env python3
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

class SOAP_Dispatcher:
	def __init__(self, address):
		self.address = address
		self.destination = '192.168.1.1'
		self.SOAP_Message = ""

	# Send/receive methods
	def send_soap_message(self):
		reply = "Error - Reply not retrieved"
		print(self.SOAP_Message)
		reply = requests.post(self.destination, timeout=5, data=self.SOAP_Message)
		try:
			reply = requests.post(self.destination, timeout=5, data=self.SOAP_Message)
		except:
			print("We excepted when POSTing, or when parsing the reply.")
		print("		Sent a SOAP Message.")
		return reply

	def flood_SOAP_Message(self, count):
		these_Status_Codes = set()
		x = 0
		failures = 0
		reply = requests.post(self.destination, timeout = 10, data=self.SOAP_Message)
		print("		This packet gets us a status_code: ", reply.status_code)
		#print "		With response: ", reply.text
		while x < count:
			#print "		Destination: ", self.destination
			try:
				reply = requests.post(self.destination, timeout = 65535, data=self.SOAP_Message)
				#print "		Posted a packet with status code: ", reply.status_code
				these_Status_Codes.add(reply.status_code)
				if 401 == reply.status_code:
					print("		Trying HTTPDigestAuth!")
					failures += 1
					reply = requests.post(self.destination, timeout=5,
						auth=HTTPDigestAuth('dsl-config', 'admin'), data=self.SOAP_Message)
					print("		Retried with HTTPDigestAuth, status code: ", reply.status_code)
				elif 200 == reply.status_code:
					self.parse_SOAP_Response(reply.text)
					pass
			except:
				print("		(!) Failure on packet no. ", x, " of ", count, ".")
				failures += 1
				if 401 == reply.status_code:
					reply = requests.post(self.destination, timeout=5,
						auth=HTTPDigestAuth('dslf-config', 'admin'), data=self.SOAP_Message)
					print("		Retried with HTTPDigestAuth, status code: ", reply.status_code)
			x += 1
			#if x % (count/10) == 0:
			#	print "		Have sent ", x, " requests out of ", count
		#print "		Sent ", count, " requests successfully."
		print("\n		", failures, " failed packets, ", count - failures, " successful.")
		return these_Status_Codes

	def send_soap_message_Digest(self, uname, password):
		reply = requests.post(self.destination, timeout=5, auth=HTTPDigestAuth(uname, password), data=self.SOAP_Message)
		print("		Sent a SOAP Message using HTTP Digest authentication, username '", uname, "' and password '", password, "'")
		return reply
