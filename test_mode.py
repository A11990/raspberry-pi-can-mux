#!/usr/bin/env python3
"""
Test mode pentru CAN MUX - fără hardware I2C
Permite testarea comunicației TCP cu Hercules
"""

import time
from ethernet_receive import EthernetReceive
from led_control import LEDControl
from config_manager import ConfigManager

# Mock classes pentru simularea hardware-ului
class MockGPIO:
    HIGH = 1
    LOW = 0
    OUT = 1
    IN = 0
    PUD_UP = 1
    BCM = 11
    
    @staticmethod
    def setmode(mode): pass
    @staticmethod
    def setwarnings(state): pass
    @staticmethod
    def setup(pin, mode, **kwargs): pass
    @staticmethod
    def output(pin, value): 
        print(f"GPIO {pin} set to {'HIGH' if value else 'LOW'}")
    @staticmethod
    def input(pin): return MockGPIO.HIGH  # Button not pressed
    @staticmethod
    def cleanup(): pass

class MockFaBoGPIO:
    def __init__(self, addr, i2c_bus=1):
        self._i2caddr = addr
        self._output = 0x00
        print(f"Mock I2C device created at address 0x{addr:02X}")
    
    def configuration(self):
        print(f"Mock configuration for device 0x{self._i2caddr:02X}")
    
    def setAllClear(self):
        print(f"Mock setAllClear for device 0x{self._i2caddr:02X}")
        self._output = 0x00
    
    def setDigital(self, port, output):
        if output:
            self._output |= port
        else:
            self._output &= ~port
        print(f"Mock setDigital: device 0x{self._i2caddr:02X}, port 0x{port:02X}, output {output}")
    
    def readOuputStatus(self, reg):
        print(f"Mock readOuputStatus: device 0x{self._i2caddr:02X}, reg 0x{reg:02X}")
        return self._output

# Monkey patch pentru testare
import sys
import gpio_pi5
import port_extender
import FaBoGPIO_PCAL6408_Modified

# Înlocuiește GPIO cu mock
gpio_pi5.GPIO = MockGPIO
gpio_pi5.GPIO_Pi5 = MockGPIO

# Înlocuiește FaBoGPIO cu mock
FaBoGPIO_PCAL6408_Modified.FaBoGPIO = MockFaBoGPIO

# Setează instanțele mock pentru port extenders
port_extender.PortExtenderMaster = MockFaBoGPIO(0x20)
port_extender.PortExtenderSlave = MockFaBoGPIO(0x21)

class TestCanMux:
    def __init__(self):
        self.ethernet = EthernetReceive()
        print("=== CAN MUX TEST MODE ===")
        print("Hardware mock-uri activate")
        
    def setup(self):
        """Setup pentru test mode"""
        print("Inițializare LED-uri... (mock)")
        print("Buton serial... (mock - not pressed)")
        print("Inițializare port extenders... (mock)")
        
        # Inițializare Ethernet (real)
        if self.ethernet.eth_init() == "RETURN_ERROR":
            print("❌ Eroare inițializare Ethernet!")
            return False
        else:
            print("✅ Ethernet inițializat cu succes!")
            return True
    
    def run(self):
        """Rulare test"""
        try:
            if not self.setup():
                return
                
            print("\n🚀 CAN MUX Test Mode pornit!")
            print("📡 Server TCP ascultă pe portul 3363")
            print("🧪 Gata pentru testare cu Hercules!")
            print("📋 Comenzi disponibile:")
            print("   - SELECT_CHANNEL: 0x01")
            print("   - GET_CHANNEL_STATUS: 0x02") 
            print("   - GET_FIRMWARE_VERSION: 0x03")
            print("\n⏹️  Apăsați Ctrl+C pentru oprire\n")
            
            while True:
                self.ethernet.eth_receive_telegram()
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\n🛑 Oprire CAN MUX Test Mode...")
            self.ethernet.cleanup()

if __name__ == "__main__":
    test_app = TestCanMux()
    test_app.run()