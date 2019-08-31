#! /usr/bin/env python 27
from GENA_Handler import *

t = GENA_Handler("192.168.1.254", 37215)
t.compile_Eventing_Packet()
t.send_Eventing_Packet()