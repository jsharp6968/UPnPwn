"""This module parses all the xml description documents and creates all of the propeties of the
UPnP devices you interact with. Strange behaviour with a given device may be due to the particular
format of the description documents, and will also depend on the version of UPnP implementation encountered.
Ideally this will become modular and use a library of schemas. Yeah, 350 lines is too big."""
#! /usr/bin/env python3
import urllib3
import xml.etree.ElementTree as ET
from UPnP_Action import *
from UPnP_Service import *
from UPnP_State_Variable import *
from UPnP_State_Variable_Table import *
from UPnP_Action_Argument import *
from UPnP_Device_InfoBundle import *
from UPnPwn_File_Handler import *

http = urllib3.PoolManager()

def fetch_SCPD_File_Contents(URL):
    """Read an xml document from a URL, root or otherwise, into a string."""
    scpd_File_Data = ""
    try:
        scpd_File_Data = http.request('GET', URL).data
    except:
        scpd_File_Data = http.request('GET', URL + '.xml').data
        print("     Nope, it was " + URL + ".xml !")
    scpd_File_Data = str(scpd_File_Data)
    scpd_File_Data = scpd_File_Data[2:-1]
    scpd_File_Data = scpd_File_Data.replace('\\r', '')
    scpd_File_Data = scpd_File_Data.replace('\\n', '')
    return scpd_File_Data

def store_SCPD_Info(address, device):
    device.device_SCPD_URL_List = device_SCPD_URL_List
    device.set_Device_Services_List(device_Services_List)
    device.device_Eventing_URL_List = device_Eventing_URL_List
    device.device_Control_URL_List = device_Control_URL_List
    device.device_Service_State_Variable_Table_List = device_Service_State_Variable_Table_List
    device.device_Service_Action_Arguments_List_List = device_Service_Action_Arguments_List_List
    device.presentation_port = presentation_port
    device.presentationURL = presentationURL
    device.device_Actions_Dictionary = device_Actions_Dictionary
    return device

def get_presentation_url(location):
    global presentationURL
    presentationURL = location[0: location.find(":", 6)]
    return presentationURL

def get_Presentation_Port(rootURL):
    rootURL = rootURL.strip()
    presentation_port = 0
    if rootURL.startswith("http"):
        port_Index = rootURL.find(":", 9)
        end_Port_Index = rootURL.find("/", port_Index)
        port_As_String = rootURL[port_Index + 1 : end_Port_Index]
        presentation_port = int(port_As_String)
        try:
            presentation_port = int(port_As_String)
            #print "        Presentation port: ",  presentation_port
        except:
            print("{!} No port found in root description URL. Assuming presentation_port is 80 (it probably isn't)")
            presentation_port = 80
        return presentation_port
    else:
        port_Index = rootURL.find(":")
        port_Index += 1
        end_Port_Index = rootURL.find("/", port_Index)
        port_As_String = rootURL[port_Index : end_Port_Index]
        try:
            presentation_port = int(port_As_String)
            #print "        Presentation port: ",  presentation_port
        except:
            print("{!} No port found in root description URL. Assuming presentation_port is 80 (it probably isn't)")
            presentation_port = 80
        return presentation_port

def read_SCPD_Root(device):
    """Read the root xml description document and prompt to save locally."""
    location = device.root_xml_location.strip()
    print("        Reading this device's root XML description document from: " + location)
    device.presentation_url = get_presentation_url(location)
    print("        Using presentation_url: " + device.presentation_url)
    device.presentation_port = get_Presentation_Port(location)
    print("        Using presentation port: " + str(device.presentation_port))

    scpd_File_Data = fetch_SCPD_File_Contents(location)
    print("        Read URL successfully!")
    #print("\n" + scpd_File_Data + "\n")
    #prompt = "        Save this root description document locally? Y/N > "
    #prompt = "\n" + prompt
    #userSelection = raw_input(prompt)
    #if userSelection.upper() == "Y":
    #    scpd_File_Name = ''.join(e for e in location if e.isalnum())
    #    save_File(scpd_File_Name, scpd_File_Data)
    #print("Root data\n\n")
    #print(scpd_File_Data)
    #print("\n\nEnd Root data\n\n")
    device = parse_Root_SCPD_XML(scpd_File_Data, device)
    device.purge_Service_Repetitions()
    device.remove_Empty_Services()
    print("     Parsed root XML and further description documents...")
    print("     Stored SCPD info...")
    return device

    #print "        You may have encountered a machine running a direct pairing service... uTorrent does this."

def update_A_Service(device, this_Service):
    """Replaces a service object with a more up-to-date version of the same object. For when you find a new
    action/state variable."""
    x = 0
    for service in device.service_list:
        if service.ST.upper().strip() == this_Service.ST.upper().strip():
            print ("        Updating a service: " + this_Service.ST)
            device.service_list[x] = this_Service
            break
        x += 1
    return device

def add_A_Service(device, this_Service):
    """Add a new service to the provided device."""
    x = 0
    for service in device.device_SSDP_Services_List:
        if service.ST.upper().strip() == this_Service.ST.upper().strip():
            print("        Adding a service: " + this_Service.ST)
            device.add_Service(this_Service)
            break
        x += 1
    return device

def check_Element_For_Services(element):
    this_Service = UPnP_Service("NULL")
    element_Tag_As_String = str(element.tag).upper()
    if element_Tag_As_String.endswith("SERVICE"):
        for l2 in element:
            if l2.tag.upper().endswith("SCPDURL"):
                print("        We found a description document!")
                #print(l2.tag.upper())
                this_Service.description_url = l2.text
            elif l2.tag.upper().endswith("CONTROLURL"):
                print("        We found a control URL!")
                this_Service.control_url = l2.text
            elif l2.tag.upper().endswith("EVENTSUBURL"):
                print("        We found an eventing subscription URL!")
                this_Service.eventing_URL = l2.text
            elif l2.tag.upper().endswith("SERVICEID"):
                print("        We found a service ID!")
                this_Service.service_id = l2.text
            elif l2.tag.upper().endswith("SERVICETYPE") or l2.tag.upper().endswith("ST"):
                print("        We found a service type!")
                this_Service.name = l2.text
                this_Service.ST = l2.text
    return this_Service

def check_Element_For_Device_SpecVersion(element):
    spec_Version_String = "NULL"
    element_Tag_As_String = str(element.tag).upper()
    if element_Tag_As_String.endswith("SPECVERSION"):
        if element[0].tag.upper() == "MAJOR":
            spec_Version_String += element[0].text
            if element[1].tag.upper() == "MINOR":
                spec_Version_String += element[1].text
    return spec_Version_String

def check_Element_For_device_infoBundle(element, this_device_infoBundle):
    element_Tag_As_String = str(element.tag).upper()
    filledFields = 0
    if element_Tag_As_String.endswith("DEVICE"):
        for subElement in element:
            if subElement.tag.upper().endswith("DEVICETYPE"):
                deviceType = subElement.text
                deviceType = deviceType.replace("urn:schemas-upnp-org:device:", "")
                deviceType = deviceType.replace("urn:dslforum-org:device:", "")
                deviceType = deviceType.replace(":1", "")
                this_device_infoBundle.deviceType = deviceType
                filledFields += 1
            elif subElement.tag.upper().endswith("FRIENDLYNAME"):
                this_device_infoBundle.friendlyName = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("MANUFACTURER"):
                this_device_infoBundle.manufacturer = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("MANUFACTURERURL"):
                this_device_infoBundle.manufacturerURL = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("MODELDESCRIPTION"):
                this_device_infoBundle.modelDescription = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("model_name"):
                this_device_infoBundle.model_name = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("MODELNUMBER"):
                this_device_infoBundle.modelNumber = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("MODELURL"):
                this_device_infoBundle.modelURL = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("SERIALNUMBER"):
                this_device_infoBundle.serialNumber = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("UDN"):
                this_device_infoBundle.UDN = subElement.text
                filledFields += 1
            elif subElement.tag.upper().endswith("UPC"):
                this_device_infoBundle.UPC = subElement.text
                filledFields += 1
    this_device_infoBundle.filledFields = filledFields
    return this_device_infoBundle

# Current code for parse_Root_SCPD_XML works with upnp.org schema for UPnP device version 1.0: <root xmlns="urn:schemas-upnp-org:device-1-0">
# This has 8 levels from the root level. Testing device is a Huawei HG659b.
#
# l1 = <SpecVersion> and <Device> - which is an Internet Gateway Device (IGD)
# l2 = <ServiceList> and useful info of IGD (serial number, device friendly name, presentation URL etc) and <deviceList> for further devices
# l3 = <Service>s from within the IGD ServiceList and <device>s in the deviceList, such as "WANDevice" and "LANDevice"
# l4 = <ServiceList>s of those further devices, and one further <deviceList>, in this case a child-device of "WANDevice"
# l5 = <Sevice>s within the ServiceLists of those other devices, and the final <device> which is a "WANConnectionDevice", and its ServiceList
# l6 = All service URLs for Services within the above ServiceLists, <Service>s within the WANConnectionDevice ServiceList
# l7 = All service URLs for Services within WANConnectionDevice
#
# The above list is very difficult to follow/visualise without an actual xml document to browse. Obviously this layout varies from schema to
# schema. The device desciption xml file URLs, control URLs and eventing URLs all live one level below the <Service> level, so you grab all three 
# at once. Note that all are relative URLs, not absolute - they have to be appended to the presentation URL. In some cases
# the <presentationURL> on l2 does not include the :port suffix - it's just an IPV4 address. This port will have to be appended to all URLs for 
# them to work.

def parse_Root_SCPD_XML(scpd_File_Data, device):
    root = ET.fromstring(scpd_File_Data)
    for l1 in root:
        # specVerions and and least one root device live here
        #print("l1 =" + l1.tag)
        specVersion = check_Element_For_Device_SpecVersion(l1)
        if specVersion != "NULL":
            device.specVersion = specVersion
            print(specVersion)
        this_device_infoBundle = UPnP_Device_InfoBundle(device.root_xml_location)
        this_device_infoBundle = check_Element_For_device_infoBundle(l1, this_device_infoBundle)
        if this_device_infoBundle.filledFields > 0:
            device.device_infoBundle = this_device_infoBundle
            print("        We filled " + str(this_device_infoBundle.filledFields) +" fields in the infobundle")
        for l2 in l1:
            for l3 in l2:
                this_Service = check_Element_For_Services(l3)
                if this_Service.name != "NULL":
                    device = add_A_Service(device, this_Service)
                for l4 in l3:
                    this_Service = check_Element_For_Services(l4)
                    if this_Service.name != "NULL":
                        device = add_A_Service(device, this_Service)
                    for l5 in l4:
                        this_Service = check_Element_For_Services(l5)
                        if this_Service.name != "NULL":
                            device = add_A_Service(device, this_Service)
                        for l6 in l5:
                            this_Service = check_Element_For_Services(l6)
                            if this_Service.name != "NULL":
                                device = add_A_Service(device, this_Service)
                            for l7 in l6:
                                this_Service = check_Element_For_Services(l7)
                                if this_Service.name != "NULL":
                                    device = add_A_Service(device, this_Service)
    print("        Set all root-XML-derived lists...")
    print("        The current device has the following number of Services: " + str(len(device.service_list)))
    device.refresh_Description_URLs()
    print("     We are handling: " + str(len(device.scpd_URL_List)) + " description document(s).\n\n")
    device = fetch_Service_Description_Documents(device.scpd_URL_List, device)
    return device

# This code for parse_SCPD_Description_Document works with upnp.org schema for a UPnP service version 1.0: <scpd xmlns="urn:schemas-upnp-org:service-1-0">
# The root level is called <scpd>. This file has 5 levels beyond root.
#
# l1 = <specVersion>, the <actionList> for this service and <serviceStateTable> for the variables which make up this service's state
# l2 = Numerous <action>s in the actionList and numerous <StateVariable>s in the serviceStateTable. Note that none yet have names.
# l3 = The <name> for each action in the actionList, the <argumentList> for each action, and the <name> and <dataType> for each state variable
# l4 = The <argument>s in each argumentList
# l5 = The <name>, <direction> and <relatedStateVariable> of each argument in an action's argument list.
#
# Note that the <direction> element on l5 refers to whether you will be reading a value FROM the server or writing a new value TO the server.
# All arguments with "in" <direction> have to be given a value in your SOAP request (at least in theory). All those with an "out" <direction>
# are listed in the SOAP request but you can (and should) send no value, ie for action <GetPublicIPAddress>, with one argument <NewPublicIPAddress>
# that has a <direction> of "out", you would send a SOAP request containing the line: 
# <NewPublicIPAddress></NewPublicIPAddress>

# The <stateVariables> have a "sendEvents" attribute. Unsure what this means, either it means you can't subscribe to it through the eventing 
# URL or nobody has subscribed yet... In the latter case it's useful for checking if any UPnP-enabled devices are subscribing to events.
# A GENA handler is in development for UPnPwn 0.4.

def parse_SCPD_Description_Document(description_File_Contents, description_Full_URL, device):
    """Parse a document referred to in the root description document. This is what creates services and fills their
    data fields with actions, arguments and state variable names/properties.
    There are probably cleaner ways to do this, and it's quite heavily dependant on a specific format."""
    current_Service = UPnP_Service("NULL")
    for this_Service in device.service_list:
        if description_Full_URL.strip().endswith(this_Service.description_url.strip()):
            current_Service = this_Service
            break
    print("     Currently parsing details for service: " + current_Service.name)
    root = ET.fromstring(description_File_Contents)
    for l1 in root:
        this_Tag1 = l1.tag.upper()
        #print("service desc l1= " + this_Tag1)
        if this_Tag1.endswith("SERVICESTATETABLE"):
            print("     Found the service's state table.")
            for l2 in l1:
                this_state_variable_table = current_Service.state_variable_table
                this_State_Variable = UPnP_State_Variable(l2[0].text.strip(), l2[1].text.strip(), l2.attrib)
                print("     Adding a state variable named " + l2[0].text.strip() + " to current service, dataType: " + l2[1].text.strip())
                this_state_variable_table.add_State_Variable(this_State_Variable)
                current_Service.state_variable_table= this_state_variable_table
                current_Service.num_state_variables = len(this_state_variable_table.variables)
                device = update_A_Service(device, current_Service)
                device.gather_Device_Statistics()
                print("     This service now has " + str(current_Service.num_state_variables) + " state variable(s) associated with it.")
        for l2 in l1:
            #print("service desc l2=" + l2.tag)
            if type(l2.text) == l2.tag:
                this_action = UPnP_Action(l2.text.strip())
            else:
                this_action = UPnP_Action("temp")
                pass
            thisTag = str(l2.tag).upper()
            if thisTag.endswith("ACTION"):
                for l3 in l2:
                    thisTag = str(l3.tag)
                    thisTag = thisTag.upper()
                    if thisTag.endswith("NAME"):
                        if l2.tag.upper().endswith("ACTION"):
                            this_action.name = l3.text.strip()
                try:
                    if l2[1].tag.upper().endswith("ARGUMENTLIST"):
                        x = 0
                        try:
                            while l2[1][x].tag.upper().endswith("ARGUMENT"):
                                this_Argument = UPnP_Action_Argument(l2[1][x][0].text.replace("New", ""))
                                this_Argument.direction = l2[1][x][1].text.strip()
                                this_Argument.related_state_variable = l2[1][x][2].text.strip()
                                #print("? " + l2[1][x][0].text)
                                #print("! " + this_Argument.name)
                                this_action.add_Argument_To_List(this_Argument)
                                x += 1
                        except:
                            print("     Going to add an Action to a Service...")
                            current_Service.add_Action(this_action)
                            print("     Successfully added Action " + this_action.name + " to Service " + current_Service.name)
                            device = update_A_Service(device, current_Service)
                            print("     Successfully updated this service!")
                except:
                    print("     Exception handling an argument list...")
                device = update_A_Service(device, current_Service)
    print("     Parsed through a description document...\n\n")
    return device

def save_SCPD_Description_Document(description_Full_URL):
    """Store an xml description document locally."""
    description_Filename = ''.join(e for e in description_Full_URL if e.isalnum())
    description_File_Contents = fetch_SCPD_File_Contents(description_Full_URL)
    description_Filename += ".xml"
    save_File(description_Filename, description_File_Contents)

def read_SCPD_Description_Document(description_Full_URL, device):
    """Fetch and parse one of the documents which is referred to in the root description document."""
    print("     Fetching: " + description_Full_URL)
    description_File_Contents = fetch_SCPD_File_Contents(description_Full_URL)
    print("     Fetched a description document...")
    device = parse_SCPD_Description_Document(description_File_Contents, description_Full_URL, device)
    return device

def fetch_Service_Description_Documents(description_Document_Relative_Paths_List, device):
    """Contstruct the URLS needed to request the description documents referred to in the root description document."""
    for description_Document_Relative_Path in description_Document_Relative_Paths_List:
        description_Full_URL = ""
        description_Full_URL = device.presentation_url + ":" + str(device.presentation_port) + description_Document_Relative_Path
        description_Full_URL = description_Full_URL.strip()
        print("     Trying this URL: " + description_Full_URL)
        device = read_SCPD_Description_Document(description_Full_URL, device)
    return device