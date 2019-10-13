"""This module defines the various errors handled by upnpwn. Lots of this module is
dedicated to UPnP stack errors and their error codes."""
#! /usr/bin/env python3

class UPnPwnError(Exception):
	"""This is the base error class."""
	pass

class UPnPError(Exception):
	"""This is an implementation of the error codes from UPnP 1.0 Specification."""
	pass