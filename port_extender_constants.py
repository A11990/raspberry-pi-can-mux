#!/usr/bin/env python3
"""
PortExtender constants - Python equivalent of PortExtender.h
Contains all constants and extern declarations
"""

# Constants (from PortExtender.h)
MASTER = 1
SLAVE = 0
MASTER_ADDRESS = 0x20
SLAVE_ADDRESS = 0x21

# Extern Variables equivalent (these will be the actual instances)
# In Python, these are imported from the actual implementation
# extern FaBoGPIO PortExtenderMaster;
# extern FaBoGPIO PortExtenderSlave;

# Extern Functions prototype equivalent (these are the actual function names)
# extern void InitPortExtender(byte lb_MasterSlave);
# extern void PortExtenderSetPin(byte lb_Pin, byte lb_MasterSlave);

# Arduino-style type definitions for compatibility
byte = int  # Arduino byte is equivalent to Python int (0-255)