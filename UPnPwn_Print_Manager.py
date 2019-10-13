"""A module for handling the various CLI print methods in one place."""
#!/usr/bin/env python3
import pyfiglet

BLOCK = "\n\n\n\n\n\n\n"

MAIN_MENU_STRING = """        Q | q | exit = Exit the program
        S | s = Scan for SSDP-responding hosts and list them
        H | h = Specify a host whose devices you want to explore\n"""

HOST_MENU_STRING = """
        D | d = Specify a device on this host whose services you want to explore
        M | m = Return to the main menu\n"""

SERVICE_MENU_STRING = """
        L | l = List all actions defined by this service (already listed above, but this clears duplicates)
        A | a = Specify an action to explore 
        R | r = Return to the device menu\n"""

DEVICE_MENU_BEFORE_SCPD_STRING = """
        The following service list was obtained from SSDP packets. This list may contain 
        devices (lines beginning with 'uuid') alongside services. The interesting details of
        UPnP services (such as action names, arguments etc) are obtained from SCPD files.
        These have not yet been fetched, so we know very little right now.\n"""

DEVICE_MENU_OPTIONS = """       L | l = List SSDP-discovered services (already listed above)
        F | f = Fetch and parse all SCPD documents
        R | r = Return to the Host menu\n"""

DEVICE_MENU_AFTER_SCPD_STRING = """
        H | h = Hail-Mary Test - Send '$(poweroff)' to every action (loud/fun)  
        L | l = List Services (already listed above)
        S | s = Specify a service to interact with
        R | r = Return to the Host menu\n"""

ACTION_MENU_STRING = """
        A | a = List arguments of this action
        H | h = Hail-Mary Test - Send '$(poweroff)' to every action (loud/fun)
        S | s = List state variables for this action
        C | c = Send SOAP commands to execute this action (fun)
        R | r = Return to the Service menu\n"""

def action_menu_print(device, this_service, this_action):
    """Print for the action menu. Requires discovery to have been done and a sensibly filled
    device object, containing services. Calls UPnP_Action object methods, which may change."""
    print(BLOCK)
    action_menu_header = "\n\n      ##### Action Menu for %s in %s on %s on %s at %s #####" % (
        this_action.name, this_service.name, device.device_infoBundle.deviceType,
        device.device_infoBundle.model_name, device.address)
    print(action_menu_header)
    print("     Which is an action of:  ", this_service.name)
    print("     Living on host:         ", device.address)
    print("     Arguments:          ", this_action.num_arguments)
    print("     State Variables:        ", this_action.num_state_variables)
    this_action.print_Action_Arguments()
    print("\n", ACTION_MENU_STRING)

def service_menu_print(device, this_service):
    """Print for the service menu. Requires discovery to have been done and a sensibly filled
    service object to be present. Calls UPnP_Service object methods, which may change."""
    print(BLOCK)
    this_service.name = this_service.name.strip()
    service_menu_header = "\n\n        ####### Service Menu for %s on %s on %s at %s #######" % (
        this_service.name, device.device_infoBundle.deviceType, device.device_infoBundle.model_name,
        device.address)
    print(service_menu_header)
    this_service.print_Service_Details()
    this_service.print_Service_Actions()
    this_service.populate_Argument_Datatypes()
    print(SERVICE_MENU_STRING)

def device_menu_before_scpd_print(device):
    """Print the device menu before SCPD documents have been fetched. Not much to display here
    aside from basic host info and the option to fetch SCPD documents. Requires a host. Uses
    UPnP_Host object methods, which may change."""
    print("        ####### Device Menu for Device-%s at %s #######" % (device.host_index + 1,
                                                                    device.address))
    print(DEVICE_MENU_BEFORE_SCPD_STRING)
    device.print_Device_SSDP_service_list()
    print(DEVICE_MENU_OPTIONS)

def device_menu_after_scpd_print(device):
    """Print the device menu with all info gained from SCPD documents. Uses many UPnP_Device
    methods, which may change."""
    print(BLOCK)
    print("        ##### Device Menu for %s on %s at %s #####" % (device.device_infoBundle.deviceType,
                                                               device.device_infoBundle.model_name,
                                                               device.address))
    device.device_infoBundle.print_InfoBundle()
    device.remove_Empty_Services()
    device.gather_Device_Statistics()
    device.print_Device_Statistics()
    device.print_Device_service_list()
    print(DEVICE_MENU_AFTER_SCPD_STRING)

def host_menu_print(host):
    """Print the host menu, which is just a UPnP_Host method to list devices, then the menu
    string."""
    print(BLOCK)
    print("\n\n     ####### Host Menu for %s #######" % host.address)
    host.print_UPnP_Device_List()
    print(HOST_MENU_STRING)

def list_hosts(this_network):
    """Lists the hosts contained within the current Network Impression. Could be made into
    a method of the UPnP_Network_Impression object."""
    print(BLOCK)
    host_index = 1
    for host in this_network.hosts_list:
        print("        +++++ Host ", host_index, " +++++")
        host.print_Basic_Host_Info()
        print("")
        for device in host.upnp_devices_list:
            device.print_Basic_Device_Info()
        print("        +++++++++++++++++++\n")
        host_index += 1

def main_menu_print():
    """Pylint won't give me 10 unless there's a docstring here ;)"""
    print(MAIN_MENU_STRING)

def do_pyfiglet(text):
    """Uses pyfiglet to print a message. It has many styles but 'letters' composes each char
    of the message of that ascii char, which is cool. Default is 'small'."""
    ascii_banner = pyfiglet.figlet_format(text, font="small")
    lines = ascii_banner.splitlines()
    for line in lines:
        print("         " + line)
