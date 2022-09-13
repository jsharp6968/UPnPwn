"""This module can construct SOAP request messages from a list of tag names. No netcode."""


class SOAP_Constructor:
    def __init__(self, address):
        self.address = address
        self.xml_declaration = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        self.SOAP_ENVELOPE_START = """%s<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/\"
   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/\">
   <s:Body>\n""" % self.xml_declaration
        self.SOAP_ENVELOPE_END = """</s:Body>
</s:Envelope>"""

    # SOAP packet component creation methods
    def set_Action_Tag_Opener(self, action_Name, service_Name):
        """This has a given xml structure as defined by the UPnP standard."""
        action_Tag_Opener = "<u:"
        action_Tag_Opener += action_Name
        action_Tag_Opener += " xmlns:u=\"urn:schemas-upnp-org:service:"
        action_Tag_Opener += service_Name
        action_Tag_Opener += ":1\">\n"
        self.action_Tag_Opener = action_Tag_Opener

    def set_Action_Tag_Closer(self, action_Name):
        """This has a given xml structure as defined by the UPnP standard."""
        action_Tag_Closer = "</u:"
        action_Tag_Closer += action_Name
        action_Tag_Closer += ">\n"
        self.action_Tag_Closer = action_Tag_Closer

    def autofill_Argument(self, argument):
        argument_Type = argument.datatype.upper()
        if "UI2" in argument_Type:
            # Unsigned 16-bit integer, max value = 65535
            return "1"
        elif "UI4" in argument_Type:
            # Unsigned 32-bit integer, max value = 4,294,967,295
            return "2"
        elif "I2" in argument_Type:
            # Signed 16-bit integer, range -32,768 to 32,767
            return "3"
        elif "I4" in argument_Type:
            # Signed 32-bit integer, range -2,147,483,648 to 2,147,483,647
            return "4"
        elif "STRING" in argument_Type:
            # Unlimited string, though UPnP requires UTF-8
            return "5"
        elif "BOOLEAN" in argument_Type:
            # Meant to be 1 for True and 0 for False, but yes/no/true/false tolerated
            return "0"
        print("        Tried to autofill argument " + argument.name +
              " but we couldn't identify the given datatype: \"" + argument_Type + "\"")
        return "Unidentified datatype"

    def set_Arguments_Body(self, arguments_List, manual_Mode, null_Mode):
        """Takes user input to fill the fields of the variables you're submitting to
		the service, or leaves it blank if there are no IN (writable) arguments."""
        arguments_body = ""
        num_Arguments_Out = 0
        arguments_Out_List = []
        for entry in arguments_List:
            if entry.direction == "out":
                num_Arguments_Out += 1
                arguments_Out_List.append(entry.name)
                argument_Opener = "<" + entry.name + ">"
                argument_Closer = "</" + entry.name + ">\n"
            else:
                argument_Opener = "<" + entry.name + ">"
                argument_Closer = "</" + entry.name + ">\n"
                if manual_Mode == 1:
                    user_Input = input("		Enter a value for %s: " % entry.name)
                    argument_Opener += user_Input
                else:
                    if null_Mode == 1:
                        pass
                    else:
                        argument_Opener += self.autofill_Argument(entry)
            arguments_body += argument_Opener
            arguments_body += argument_Closer
        self.arguments_body = arguments_body
        self.num_Arguments_Out = num_Arguments_Out
        self.arguments_Out_List = arguments_Out_List

    def set_Arguments_Body_XXE(self, arguments_List, injection_reference):
        """Submits &xxe; as the value for every argument, regardless whether it's IN or OUT."""
        arguments_body = ""
        num_Arguments_Out = 0
        arguments_Out_List = []
        for entry in arguments_List:
            argument_Opener = "<" + entry.name + ">" + injection_reference
            argument_Closer = "</" + entry.name + ">\n"
            arguments_body += argument_Opener
            arguments_body += argument_Closer
        self.arguments_body = arguments_body
        self.num_Arguments_Out = num_Arguments_Out
        self.arguments_Out_List = arguments_Out_List

    def set_Control_URL(self, control_url):
        self.control_url = control_url

    def set_Control_Port(self, control_Port):
        self.control_Port = str(control_Port)

    def set_SOAP_Destination(self):
        destination = "http://"
        destination += str(self.address)
        destination += ":"
        destination += self.control_Port
        destination += self.control_url
        self.destination = destination

    # SOAP packet compilation methods
    def compile_SOAP_Message(self):
        """Add the pieces of a SOAP packet together in sequence and call that a SOAP message."""
        SOAP_Message = ""
        SOAP_Message += self.SOAP_ENVELOPE_START
        SOAP_Message += self.action_Tag_Opener
        SOAP_Message += self.arguments_body
        SOAP_Message += self.action_Tag_Closer
        SOAP_Message += self.SOAP_ENVELOPE_END
        self.SOAP_Message = SOAP_Message

    def prepare_clean_soap(self, device, this_action, this_Service, manual_Mode, null_Mode):
        self.set_Action_Tag_Opener(this_action.name, this_Service.name)
        self.set_Action_Tag_Closer(this_action.name)
        self.set_Arguments_Body(this_action.arguments, manual_Mode, null_Mode)
        self.set_Control_URL(this_Service.control_url)
        self.set_Control_Port(device.presentation_port)
        self.set_SOAP_Destination()
        self.compile_SOAP_Message()

    def prepare_xxe_soap(self, device, this_action, this_Service, injection_reference):
        self.set_Action_Tag_Opener(this_action.name, this_Service.name)
        self.set_Action_Tag_Closer(this_action.name)
        self.set_Arguments_Body_XXE(this_action.arguments, injection_reference)
        self.set_Control_URL(this_Service.control_url)
        self.set_Control_Port(device.presentation_port)
        self.set_SOAP_Destination()
        self.compile_SOAP_Message()
