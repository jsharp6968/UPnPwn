"""File operations module. Allows the output of various files."""
from pathlib import Path


def save_soap_message(device, this_action, this_service, soap_message):
    """Save a local .pwn file. I didn't make a standard for this file, really it's just a textfile
    but in a syntax which upnpwn can pick up and use, so the extension is just a marker."""
    name = (this_action.name.replace(" ", "_") + "_" + this_service.name.replace(" ", "_")
            + "_" + device.device_infoBundle.deviceType.replace(" ", "_") + "_SOAP.pwn")
    save_file(name, soap_message)

def create_output_dir():
    output_dir_path = Path("../output")
    if not output_dir_path.exists():
        output_dir_path.mkdir()
    else:
        print("        Found UPnPwn output file directory!\n")

def save_file(filename, file_data):
    """Generic file method - will output whatever you want into the current directory."""
    filename = "../output/" + filename
    with open(filename, 'w') as file:
        file.write(str(file_data))
        