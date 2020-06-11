"""This module defines the SOAP_Handler class, and contains useful strings for SOAP packets."""
#! /usr/bin/env python3
#from SOAP_Constructor import prepare_auto_soap, prepare_clean_soap
from SOAP_Dispatcher import SOAP_Dispatcher
from SOAP_Constructor import SOAP_Constructor
from soap_parser import SOAP_Parser
from UPnPwn_File_Handler import save_soap_message
from errors import UPnPwnError
SOAP_ENVELOPE_START = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/\"
   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/\">
   <s:Body>"""
SOAP_ENVELOPE_END = """</s:Body>
</s:Envelope>"""

class SOAPHandler:
    """This class handles the high-level organisation of a SOAP transaction. You can hit switches
    for clean (playing by the rules) or dirty SOAP (trying to break things). There's also support
    for auto-filling packet contents, though this will be handled through sfuzz soon."""
    def __init__(self, address_string):
        self.address_string = address_string
        self.control_port = 0
        self.control_url = ""
        self.root_url = ""
        self.soap_envelope_start = SOAP_ENVELOPE_START
        self.soap_envelope_end = SOAP_ENVELOPE_END
        self.soap_message = ""

    def handle_clean_soap(self, this_device, this_action, this_service, save_message):
        """Largely deprecated, this is the same as above but only uses clean SOAP."""
        soap_dispatcher = SOAP_Dispatcher(this_device.address)
        soap_constructor = SOAP_Constructor(this_device.address) 
        soap_parser = SOAP_Parser()
        these_status_codes = set()
        soap_constructor.prepare_clean_soap(this_device, this_action, this_service)
        soap_dispatcher.destination = soap_constructor.destination
        soap_dispatcher.SOAP_Message = soap_constructor.SOAP_Message
        soap_parser.arguments_Out_List = soap_constructor.arguments_Out_List
        try:
            reply = soap_dispatcher.send_soap_message(this_service.ST, this_action.name)
            these_status_codes.add(reply.status_code)
            print("      HTTP Response: " + str(reply.status_code) + "\n")
            if reply.status_code == 200:
                soap_responses = soap_parser.parse_SOAP_Response(reply.text)
                for entry, value in list(soap_responses.items()):
                    for variable in this_service.state_variable_table.variables:
                        if entry == variable.name:
                            variable.set_Value(value)
                            #print("matched a variable")
        except UPnPwnError:
            print("     Error during SOAP transaction. Check network.")
        if save_message == 1:
            save_soap_message(this_device, this_action, this_service, soap_dispatcher.SOAP_Message)
        return these_status_codes

    def handle_soap(self, device, this_action, this_service):
        """An entry point for the main SOAP handling method, allows you to hit switches to choose
        SOAP type."""
        #selection = raw_input("        A = Automatic, else manual > ")
        soap_constructor = SOAP_Constructor()
        selection = "A"
        if "D" in selection.upper():
            print("     This is dirty soap!")
            return 0
        if "A" in selection.upper():
            soap_constructor.prepare_auto_soap(device, this_action, this_service)
            self.handle_clean_soap(device, this_action, this_service)
            print("     This is automatic soap!")
            return 0
        self.handle_clean_soap(device, this_action, this_service)
        return 0
