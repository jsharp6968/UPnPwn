"""
        UPnPwn is a client for manually interacting with UPnP servers and clients.
        It supports SSDP, SCPD XML fetching and parsing, SOAP requests and (untested) GENA Eventing.
        Some day, it'll break UPnP the way sqlmap breaks poorly sanitised SQL."""
#!/usr/bin/env python3
import re
from ssdp_Discover import ssdp_discover
from scpd_Handler import read_SCPD_Root
from SOAP_Handler import SOAPHandler
from UPnPwn_Profiler import UPnPwn_Profiler
from UPnP_Network_Impression import UPnPNetworkImpression
from UPnPwn_Print_Manager import (action_menu_print, host_menu_print, profile_menu_print,
                                  service_menu_print, list_hosts, device_menu_after_scpd_print,
                                  device_menu_before_scpd_print, main_menu_print, do_pyfiglet)

__author__ = "Jordan Sharp"
__copyright__ = "Copyright 2018"
__credits__ = ["Jordan Sharp"]
__license__ = "GPL"
__version__ = "Version 0.5"
__maintainer__ = "Jordan Sharp"
__email__ = "0xsee4@gmail.com"
__status__ = "Alpha"
TITLE_STRING = "        ####### UPnPwn %s #######" % __version__

def input_handler(prompt):
    """Eats non-string input.
    Casts everything to uppercase to dodge the problem
    of case handling. This is lazy.
    Checks every run for 'Q' or 'EXIT'."""
    prompt = "\n" + prompt + " > "
    user_selection = ""
    user_selection = input(prompt)


    if isinstance(user_selection, str) == False:
        return ""

    user_selection = user_selection.upper()

    if "Q" in user_selection or "EXIT" in user_selection:
        print("Exiting UPnPwn.")
        exit()
    return user_selection

def explore_action(device, this_service, action_name):
    """Call a given action on a given service within the appropriate device.
    This is where the action happens... no pun intended.
    It's where you'll spend most of your time when interacting with a new device.
    As such it makes sense to add functionality to it.
    """
    this_action = this_service.get_Action_By_Name(action_name)
    user_selection = ""
    prompt = "  Action: %s      Service: %s     On: %s@%s" % (this_action.name,
                                                              this_service.name,
                                                              device.device_infoBundle.deviceType,
                                                              device.address)
    while "Q" not in user_selection:
        action_menu_print(device, this_service, this_action)
        user_selection = input_handler(prompt)
        if isinstance(user_selection, str) == False:
            pass
        elif "A" in user_selection:
            # Display the arguments of an action.
            if this_action.arguments:
                print("""     This action takes no arguments.
                      As an action, it takes itself a bit seriously...""")
            else:
                this_action.print_Action_Arguments()
        elif "S" in user_selection:
            # Display the state variables referenced by an action.
            if len(this_action.state_variable_table.variables) < 1:
                print("     (!) No state variables are listed for this action.")
            else:
                this_action.state_variable_table.print_State_Variables()
        elif "C" in user_selection:
            # Send SOAP commands.
            user_selection = input_handler("      Save SOAP packet? y/n")
            dont_drop_it = SOAPHandler(device.address)
            if "Y" in user_selection:
                dont_drop_it.handle_clean_soap(device, this_action, this_service, 1, 1, 0)
            else:
                dont_drop_it.handle_clean_soap(device, this_action, this_service, 0, 1, 0)
            this_action.state_variable_table.print_State_Variables()
        elif "R" in user_selection:
            return 0

def explore_service(device, service_id):
    """Navigate a service on a given device."""
    this_service = device.service_list[service_id]
    displayed_action_names = []
    for entry in this_service.actions:
        displayed_action_names.append(entry.name)
    prompt = "      Service: %s   On: %s@%s" % (this_service.name,
                                                device.device_infoBundle.deviceType,
                                                device.address)
    user_selection = ""
    while "Q" not in user_selection:
        service_menu_print(device, this_service)
        user_selection = input_handler(prompt)
        if isinstance(user_selection, str) == False:
            # Eat non-string input.
            pass
        elif "H" in user_selection:
            # Return to Host menu.
            return 0
        if "M" in user_selection:
            main_menu()
        elif "L" in user_selection:
            # List actions, print menu again.
            this_service.print_Service_Actions()
        elif "A" in user_selection:
            # Select an action. If an int is entered after 'a' ie 'a3' then
            # the corresponding action is selected, else you're prompted.
            # Print the menu on return.
            if re.search(r'\d+', user_selection):
                choice_list = re.findall(r'\d+', user_selection)
                choice = int(choice_list[0])
                explore_action(device, this_service, displayed_action_names[choice -1])
            else:
                user_selection_int = int(input("      Enter action ID > "))
                explore_action(device, this_service, displayed_action_names[user_selection_int - 1])
        elif "R" in user_selection:
            # Return to the device menu
            return 0

def profile_device(device):
    prompt = "      %s@%s" % (device.device_infoBundle.deviceType, device.address)
    user_selection = ""
    this_Profiler = UPnPwn_Profiler(device)
    while "Q" not in user_selection:
        profile_menu_print(device)
        user_selection = input_handler(prompt)
        if "P" in user_selection:
            this_Profiler.profile_Mute_Actions()
        elif "N" in user_selection:
            this_Profiler.profile_Null_Actions()
        elif "S" in user_selection:
            this_Profiler.print_All_State_Variables()
        elif "R" in user_selection:
            return 0


def explore_device_after_scpd(device):
    """Allows you to choose a service to interact with, alongside
    a list of information about the device like serial numbers, model
    nummbers, firmware codes etc.

    This is also where you can enter attack and profile modes."""
    prompt = "      %s@%s" % (device.device_infoBundle.deviceType, device.address)
    user_selection = ""
    while "Q" not in user_selection:
        device_menu_after_scpd_print(device)
        user_selection = input_handler(prompt)
        if isinstance(user_selection, str) == False:
            pass
        elif "L" in user_selection:
            device.print_Device_service_list()
        elif "S" in user_selection:
            if device.num_services == 1:
                print("     Only 1 service detected, automatically selecting that one.")
                explore_service(device, 0)
                user_selection = ""
            else:
                if re.search(r'\d+', user_selection):
                    choice_list = re.findall(r'\d+', user_selection)
                    choice = int(choice_list[0])
                    explore_service(device, choice -1)
                else:
                    user_selection_int = int(input("      Enter Service ID > "))
                    explore_service(device, user_selection_int - 1)
        elif "P" in user_selection:
            profile_device(device)
        elif "R" in user_selection:
            return 0

def explore_device(device):
    """Offers the option of fetching SCPD documents, then
    branches to method above, explore_device_after_scpd, whiich
    has actual functions."""
    user_selection = ""
    scpd_has_been_fetched = device.scpd_has_been_fetched
    while "Q" not in user_selection:
        if scpd_has_been_fetched:
            user_selection = input_handler("        Proceed to populated device menu? Y/N")
            if "Y" in user_selection:
                explore_device_after_scpd(device)
            else:
                return 0
        else:
            device_menu_before_scpd_print(device)
            prompt = "      Device-%s@%s" % (device.host_index +1, device.address)
            user_selection = input_handler(prompt)
            if "F" in user_selection:
                # Fetch SCPD documents.
                device.scpd_has_been_fetched = True
                device = read_SCPD_Root(device)
                print("        Fetched and parsed all SCPD documents!")
                scpd_has_been_fetched = True
                do_pyfiglet("\n\nReady to Pwn")
            elif "L" in user_selection:
                device.print_Device_SSDP_service_list()
            elif "R" in user_selection:
                return 0

def explore_host(host):
    """Eats non-strings, loops input same as main_menu.
    -  D is for selecting a device, return to the main menu"""
    user_selection = ""
    while "Q" not in user_selection:
        host_menu_print(host)
        user_selection = input_handler("      %s" % host.address)
        if isinstance(user_selection, str) == False:
            pass
        elif "D" in user_selection:
            if host.num_UPnP_Devices == 1:
                print("       Only 1 device detected, automatically selecting that one.")
                device = host.upnp_devices_list[0]
            elif re.search(r'\d+', user_selection):
                choice_list = re.findall(r'\d+', user_selection)
                choice = int(choice_list[0])
                device = host.upnp_devices_list[choice -1]
            else:
                user_selection_int = int(input("      Enter device index > "))
                device = host.upnp_devices_list[user_selection_int -1]
            explore_device(device)
        elif "M" in user_selection:
            return 0

def main_menu():
    """Creates a blank Network Impression object with id of 0. This is the network.
    Infinitely loops on input until q or exit are detected, case insensitive.
    - Iterates a query on a string for the presence of commands
    - Each command is one letter
    - Does not allow multiple options, the first detected is selected
    - Eats non-strings
    """
    # - Instantiates a Network Impression.
    this_network = UPnPNetworkImpression(0)
    user_selection = ""
    while "Q" not in user_selection:
        # - Iterates a query on a string for the presence of commands. Each command is one letter.
        # Does not allow multiple options, the first detected is selected. Eats non-strings.
        main_menu_print()
        user_selection = input_handler("        UPnPwn")
        if isinstance(user_selection, str) == False:
            pass
        elif "S" in user_selection:
            # Re-uses this_network so it gets wiped each scan.
            this_network = ssdp_discover(this_network)
            list_hosts(this_network)
        elif "H" in user_selection:
            if this_network.num_hosts == 1:
                print("        Only 1 host detected, automatically selecting that one.")
                explore_host(this_network.hosts_list[0])
            else:
                user_selection = int(input("      Enter host ID > "))
                explore_host(this_network.hosts_list[user_selection - 1])

def main():
    """Prints info and goes into main_menu, which loops. Zero Input."""
    print(__doc__)
    print("\n\n")
    do_pyfiglet("UPnPwn")
    print("\n\n")
    print("        " + __version__)
    print("        " + __email__)
    print("        " + __author__)
    print("\n\n")
    main_menu()

if __name__ == '__main__':
    main()
