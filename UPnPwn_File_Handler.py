"""File operations module. Allows the output of various files."""
#! /usr/bin/env python37

def save_soap_message(device, this_action, this_service, soap_message):
    """Save a local .pwn file. I didn't make a standard for this file, really it's just a textfile
    but in a syntax which upnpwn can pick up and use, so the extension is just a marker."""
    name = (this_action.name.replace(" ", "_") + "_" + this_service.name.replace(" ", "_")
            + "_" + device.device_InfoBundle.deviceType.replace(" ", "_") + "_SOAP.pwn")
    save_file(name, soap_message)

def save_file(filename, file_data):
    """Generic file method - will output whatever you want into the current directory."""
    with open(filename, 'w') as file:
        file.write(str(file_data))
        