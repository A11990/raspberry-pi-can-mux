#!/usr/bin/env python3
"""
FaBoGPIO_PCAL6408_Modified.py
Python port of FaBoGPIO_PCAL6408_Modified.cpp
Exact equivalent of the Arduino library
"""

import smbus2 as smbus
import time

# Register Addresses (from FaBoGPIO_PCAL6408_Modified.h)
PCAL6408_OUTPUT_REG = 0x01
PCAL6408_CONFIGURATION_REG = 0x03

# OUTPUT Parameter (from .h file)
PCAL6408_IO0_OUTPUT = 0b00000000
PCAL6408_IO0_INPUT  = 0b00000001
PCAL6408_IO1_OUTPUT = 0b00000000
PCAL6408_IO1_INPUT  = 0b00000010
PCAL6408_IO2_OUTPUT = 0b00000000
PCAL6408_IO2_INPUT  = 0b00000100
PCAL6408_IO3_OUTPUT = 0b00000000
PCAL6408_IO3_INPUT  = 0b00001000
PCAL6408_IO4_OUTPUT = 0b00000000
PCAL6408_IO4_INPUT  = 0b00010000
PCAL6408_IO5_OUTPUT = 0b00000000
PCAL6408_IO5_INPUT  = 0b00100000
PCAL6408_IO6_OUTPUT = 0b00000000
PCAL6408_IO6_INPUT  = 0b01000000
PCAL6408_IO7_OUTPUT = 0b00000000
PCAL6408_IO7_INPUT  = 0b10000000

# Pin definitions (from .h file)
PCAL6408_IO0 = 0b00000001
PCAL6408_IO1 = 0b00000010
PCAL6408_IO2 = 0b00000100
PCAL6408_IO3 = 0b00001000
PCAL6408_IO4 = 0b00010000
PCAL6408_IO5 = 0b00100000
PCAL6408_IO6 = 0b01000000
PCAL6408_IO7 = 0b10000000

# Arduino constants
HIGH = 1
LOW = 0

class FaBoGPIO:
    """
    FaBo GPIO I2C Control class
    Python equivalent of Arduino FaBoGPIO class
    """
    
    def __init__(self, addr, i2c_bus=1):
        """
        Constructor - equivalent to FaBoGPIO::FaBoGPIO(uint8_t addr)
        """
        self._i2caddr = addr
        self._output = 0x00
        try:
            # Wire.begin() equivalent
            self.bus = smbus.SMBus(i2c_bus)
        except Exception as e:
            print(f"Error initializing I2C for address 0x{addr:02X}: {e}")
            self.bus = None
    
    def configuration(self):
        """
        Configure Device - equivalent to FaBoGPIO::configuration()
        """
        if not self.bus:
            return
            
        try:
            # Exact same logic as Arduino code
            conf = PCAL6408_IO0_OUTPUT
            conf |= PCAL6408_IO1_OUTPUT
            conf |= PCAL6408_IO2_OUTPUT
            conf |= PCAL6408_IO3_OUTPUT
            conf |= PCAL6408_IO4_OUTPUT
            conf |= PCAL6408_IO5_OUTPUT
            conf |= PCAL6408_IO6_OUTPUT
            conf |= PCAL6408_IO7_OUTPUT
            
            self.writeI2c(PCAL6408_CONFIGURATION_REG, conf)
            
        except Exception as e:
            print(f"Configuration error for device 0x{self._i2caddr:02X}: {e}")
    
    def setDigital(self, port, output):
        """
        Set Port to Digital - equivalent to FaBoGPIO::setDigital(uint8_t port, uint8_t output)
        """
        if not self.bus:
            return
            
        try:
            # Exact same logic as Arduino code
            if output == HIGH:
                self._output |= port
            elif output == LOW:
                self._output &= ~port
                
            self.writeI2c(PCAL6408_OUTPUT_REG, self._output)
            
        except Exception as e:
            print(f"setDigital error for device 0x{self._i2caddr:02X}: {e}")
    
    def setAllClear(self):
        """
        All Port to LOW - equivalent to FaBoGPIO::setAllClear()
        """
        if not self.bus:
            return
            
        try:
            # Exact same logic as Arduino code
            self.writeI2c(PCAL6408_OUTPUT_REG, 0x00)
            self._output = 0x00
            
        except Exception as e:
            print(f"setAllClear error for device 0x{self._i2caddr:02X}: {e}")
    
    def setGPIO(self, output):
        """
        Set Port to GPIO - equivalent to FaBoGPIO::setGPIO(uint8_t output)
        """
        if not self.bus:
            return
            
        try:
            self.writeI2c(PCAL6408_OUTPUT_REG, output)
            
        except Exception as e:
            print(f"setGPIO error for device 0x{self._i2caddr:02X}: {e}")
    
    def scanI2cAll(self):
        """
        Scan all I2C addresses - equivalent to FaBoGPIO::scanI2cAll()
        """
        device = 0
        
        for address in range(1, 127):
            error = self.scanI2cAddress(address)
            
            if error == 0:
                device += 1
                
            # Debug output (equivalent to Arduino #ifdef debug)
            # Uncomment for detailed debugging like Arduino version
            # if error == 0:
            #     print(f"I2C device found at address 0x{address:02X}")
            # elif error == 1:
            #     print(f"Data too long to fit in transmit buffer at address 0x{address:02X}")
            # elif error == 2:
            #     print(f"Received NACK on transmit of address 0x{address:02X}")
            # elif error == 3:
            #     print(f"Received NACK on transmit of data at address 0x{address:02X}")
            # elif error == 4:
            #     print(f"Other error 0x{address:02X}")
            # elif error == 5:
            #     print(f"Timeout at 0x{address:02X}")
        
        return device
    
    def scanI2cAddress(self, address):
        """
        Scan I2C Address - equivalent to FaBoGPIO::scanI2cAddress(byte address)
        """
        if not self.bus:
            return 4
            
        try:
            # Wire.beginTransmission + Wire.endTransmission equivalent
            self.bus.read_byte(address)
            return 0  # Success
            
        except Exception as e:
            # Map Python I2C errors to Arduino Wire library error codes
            error_str = str(e).lower()
            if "remote i/o error" in error_str:
                return 2  # NACK on transmit of address
            elif "input/output error" in error_str:
                return 5  # Timeout
            else:
                return 4  # Other error
    
    def readOuputStatus(self, address):
        """
        Read output status - equivalent to FaBoGPIO::readOuputStatus(uint8_t address)
        Note: Keeping the Arduino typo "Ouput" for exact compatibility
        """
        if not self.bus:
            return 0
            
        try:
            # Exact same logic as Arduino code
            data = self.bus.read_byte_data(self._i2caddr, address)
            return data
            
        except Exception as e:
            print(f"readOuputStatus error for device 0x{self._i2caddr:02X}: {e}")
            return 0
    
    def writeI2c(self, address, data):
        """
        Write I2C - equivalent to FaBoGPIO::writeI2c(uint8_t address, uint8_t data)
        """
        if not self.bus:
            return
            
        try:
            # Arduino: Wire.beginTransmission + Wire.write + Wire.endTransmission
            self.bus.write_byte_data(self._i2caddr, address, data)
            
        except Exception as e:
            print(f"writeI2c error for device 0x{self._i2caddr:02X}, reg 0x{address:02X}: {e}")