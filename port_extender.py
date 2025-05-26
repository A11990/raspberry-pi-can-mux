#!/usr/bin/env python3
"""
PortExtender.py - Python port of PortExtender.cpp
Handles PCAL6408 I2C port extender control using FaBoGPIO library
"""

from FaBoGPIO_PCAL6408_Modified import (
    FaBoGPIO, PCAL6408_IO0, PCAL6408_IO1, PCAL6408_IO2, PCAL6408_IO3,
    PCAL6408_IO4, PCAL6408_IO5, PCAL6408_IO6, PCAL6408_IO7,
    PCAL6408_OUTPUT_REG, HIGH, LOW
)

# Constants (from PortExtender.h)
MASTER = 1
SLAVE = 0
MASTER_ADDRESS = 0x20
SLAVE_ADDRESS = 0x21

# Global Variables (equivalent to Arduino global variables)
PortExtenderMaster = None
PortExtenderSlave = None

def init_port_extenders(i2c_bus=1):
    """
    Initialize global port extender instances
    Call this once at startup (equivalent to Arduino global variable creation)
    """
    global PortExtenderMaster, PortExtenderSlave
    PortExtenderMaster = FaBoGPIO(MASTER_ADDRESS, i2c_bus)
    PortExtenderSlave = FaBoGPIO(SLAVE_ADDRESS, i2c_bus)

def InitPortExtender(lb_MasterSlave):
    """
    Initialize port extender - equivalent to InitPortExtender(byte lb_MasterSlave)
    Exact same function name and logic as Arduino
    """
    global PortExtenderMaster, PortExtenderSlave
    
    # Ensure global instances are created
    if PortExtenderMaster is None or PortExtenderSlave is None:
        init_port_extenders()
    
    if lb_MasterSlave == MASTER:
        PortExtenderMaster.configuration()
        # Clear all ports
        PortExtenderMaster.setAllClear()
    else:
        PortExtenderSlave.configuration()
        # Clear all ports
        PortExtenderSlave.setAllClear()

def PortExtenderSetPin(lb_Pin, lb_MasterSlave):
    """
    Set pin - equivalent to PortExtenderSetPin(byte lb_Pin, byte lb_MasterSlave)
    Exact same function name and logic as Arduino
    """
    global PortExtenderMaster, PortExtenderSlave
    
    # Clear all ports first (same logic as Arduino)
    if lb_MasterSlave == MASTER:
        PortExtenderMaster.setAllClear()
        # Ports have already been cleared and there are no new port to set
        if lb_Pin != 0:
            # Exact same switch logic as Arduino
            if lb_Pin == 1:
                PortExtenderMaster.setDigital(PCAL6408_IO0, HIGH)
            elif lb_Pin == 2:
                PortExtenderMaster.setDigital(PCAL6408_IO1, HIGH)
            elif lb_Pin == 3:
                PortExtenderMaster.setDigital(PCAL6408_IO2, HIGH)
            elif lb_Pin == 4:
                PortExtenderMaster.setDigital(PCAL6408_IO3, HIGH)
            elif lb_Pin == 5:
                PortExtenderMaster.setDigital(PCAL6408_IO4, HIGH)
            elif lb_Pin == 6:
                PortExtenderMaster.setDigital(PCAL6408_IO5, HIGH)
            elif lb_Pin == 7:
                PortExtenderMaster.setDigital(PCAL6408_IO6, HIGH)
            elif lb_Pin == 8:
                PortExtenderMaster.setDigital(PCAL6408_IO7, HIGH)
            # default case - do nothing (same as Arduino)
    
    if lb_MasterSlave == SLAVE:
        PortExtenderSlave.setAllClear()
        # Ports have already been cleared and there are no new port to set
        if lb_Pin != 0:
            # Exact same switch logic as Arduino
            if lb_Pin == 1:
                PortExtenderSlave.setDigital(PCAL6408_IO0, HIGH)
            elif lb_Pin == 2:
                PortExtenderSlave.setDigital(PCAL6408_IO1, HIGH)
            elif lb_Pin == 3:
                PortExtenderSlave.setDigital(PCAL6408_IO2, HIGH)
            elif lb_Pin == 4:
                PortExtenderSlave.setDigital(PCAL6408_IO3, HIGH)
            elif lb_Pin == 5:
                PortExtenderSlave.setDigital(PCAL6408_IO4, HIGH)
            elif lb_Pin == 6:
                PortExtenderSlave.setDigital(PCAL6408_IO5, HIGH)
            elif lb_Pin == 7:
                PortExtenderSlave.setDigital(PCAL6408_IO6, HIGH)
            elif lb_Pin == 8:
                PortExtenderSlave.setDigital(PCAL6408_IO7, HIGH)
            # default case - do nothing (same as Arduino)


# Class wrapper for object-oriented usage (optional, for compatibility)
class PortExtender:
    """
    Optional class wrapper for PortExtender functionality
    Provides both functional and OOP interfaces
    """
    
    def __init__(self, i2c_bus=1):
        init_port_extenders(i2c_bus)
    
    def init_port_extender(self, master_slave):
        """Wrapper for InitPortExtender function"""
        if master_slave == "MASTER":
            InitPortExtender(MASTER)
        elif master_slave == "SLAVE":
            InitPortExtender(SLAVE)
        else:
            InitPortExtender(master_slave)
    
    def set_pin(self, pin, master_slave):
        """Wrapper for PortExtenderSetPin function"""
        if master_slave == "MASTER":
            PortExtenderSetPin(pin, MASTER)
        elif master_slave == "SLAVE":
            PortExtenderSetPin(pin, SLAVE)
        else:
            PortExtenderSetPin(pin, master_slave)
    
    def read_output_status(self, master_slave):
        """Read current output status"""
        global PortExtenderMaster, PortExtenderSlave
        
        if master_slave == "MASTER" or master_slave == MASTER:
            return PortExtenderMaster.readOuputStatus(PCAL6408_OUTPUT_REG)
        else:
            return PortExtenderSlave.readOuputStatus(PCAL6408_OUTPUT_REG)