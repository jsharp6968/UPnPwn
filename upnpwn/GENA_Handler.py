#! /usr/bin/env python3
from socket import *

### Example subscription packet
# SUBSCRIBE publisher path HTTP/1.1
# HOST: publisher host:publisher port
# USER-AGENT: OS/version UPnP/1.1 product/version
# CALLBACK: <delivery URL>
# NT: upnp:event

eventing_Packet_Start = "SUBSCRIBE "
eventing_Packet_HTTP = " HTTP/1.1"
eventing_Packet_Notification_Type_Header = "\nNotification-Type: gena:update"
eventing_Packet_Host_Header = "\nHOST: 192.168.1.1:37215"
eventing_Packet_Timeout_Header = "\nTIMEOUT: Second-60"
eventing_Packet_Subscription_Lifetime_Header = "\nSubscription-Lifetime: 600"
eventing_Packet_Delivery_Control_Header = "\n Delivery-control: "
eventing_Packet_Notification_Version_Header = "\nNotification-Version: 1.0"
eventing_Packet_Host = "\nHOST: "
eventing_Packet_User_Agent = "\nUSER-AGENT: UPnPwn 0.3"
eventing_Packet_Callback = "\nCALLBACK: "
eventing_Packet_NT = "\nNT: upnp:event"

class GENA_Handler:
	def __init__(self, address, eventing_Port):
		self.address = address
		self.eventing_Port = eventing_Port
		self.eventing_Host = address + ":" + str(eventing_Port)
		self.eventing_URL = "" 

	def set_Eventing_Port(self, eventing_Port):
		self.eventing_Port = eventing_Port

	def set_Eventing_URL(self, eventing_URL):
		self.eventing_URL = eventing_URL

	def set_Eventing_Host(self):
		self.eventing_Host = self.address + ":" + str(self.eventing_Port)

	def set_Callback_URL(self, callback_URL):
		self.callback_URL = callback_URL

#SUBSCRIBE URI HTTP/1.1
#     Notification-Type: CoreNotificationType
#     Call-back: URI [ URI  ]
#     Delivery-control: poll-interval = seconds
#     Subscription-Lifetime: seconds
#     Notification-Version: 1.0

	def compile_Eventing_Packet(self):
		eventing_Packet = ""
		eventing_Packet += eventing_Packet_Start
		eventing_Packet += "/event/WANIPConnection"
		eventing_Packet += eventing_Packet_HTTP
		#eventing_Packet += eventing_Packet_Notification_Type_Header
		#eventing_Packet += eventing_Packet_Host
		#eventing_Packet += self.eventing_Host
		#eventing_Packet += eventing_Packet_User_Agent
		#eventing_Packet += eventing_Packet_Timeout_Header
		eventing_Packet += eventing_Packet_Host_Header
		eventing_Packet += eventing_Packet_Callback
		eventing_Packet += "<192.168.1.4/test>"
		#eventing_Packet += eventing_Packet_Subscription_Lifetime_Header
		#eventing_Packet += eventing_Packet_Notification_Version_Header
		eventing_Packet += eventing_Packet_NT
		#eventing_Packet += "\nTIMEOUT: Second-900"
		eventing_Packet += "\n\n"
		self.eventing_Packet = eventing_Packet

	def send_Eventing_Packet(self):
		#eventing_Socket = socket(AF_INET, SOCK_STREAM)
		#listening_Socket = socket(AF_INET, SOCK_STREAM)
		#eventing_Socket.settimeout(5)
		print(self.eventing_Packet)
		#eventing_Socket.sendto(self.eventing_Packet, (self.address, self.eventing_Port))
		#eventing_Socket = socket(AF_INET, SOCK_STREAM)
		#eventing_Socket.bind(('0.0.0.0', 34215))
		#eventing_Socket.connect(("192.168.1.254", 37215))
		#eventing_Socket.sendto(self.eventing_Packet, ("192.168.1.254", 37215))
		while True:
			try:
				eventing_Socket = socket(AF_INET, SOCK_STREAM)
				eventing_Socket.settimeout(5)
				eventing_Socket.bind(('0.0.0.0', 35215))
				eventing_Socket.connect(("192.168.1.1", 80))
				eventing_Socket.send(self.eventing_Packet)
				data, addr = eventing_Socket.recvfrom(1500)
				print(data)
				break
				#eventing_Socket.close()
			except timeout:
				#eventing_Socket.close()
				print("Timed out.")
				break
		#listening_Socket.bind((gethostname(), 38215))
		#data, addr = listening_Socket.recvfrom(1500)
		#print "Got response from ", addr
		#print "Data: ", data
		#while True:
		#	try:
		#		print "Listening..."
		#		data, addr = eventing_Socket.recvfrom(1500)
		#		print "Got response from ", addr
		#		print "Data: ", data
		#	except timeout:
		#		print "Socket timed out."