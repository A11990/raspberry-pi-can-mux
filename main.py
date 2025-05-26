#!/usr/bin/env python3
"""
CAN MUX - Raspberry Pi Python Port
Main application file - equivalent to CanMux.ino
"""

import time
from gpio_pi5 import GPIO, digitalWrite, digitalRead, pinMode, delay
from ethernet_receive import EthernetReceive
from led_control import LEDControl
from serial_menu import SerialMenu
from port_extender import InitPortExtender, MASTER, SLAVE

# Arduino-like constants
SERIAL_MODE_BUTTON_PORT = 18  # BCM pin 18 (equivalent to A0)

class CanMux:
    def __init__(self):
        self.led = LEDControl()
        self.ethernet = EthernetReceive()
        self.serial_menu = SerialMenu()
        
    def setup(self):
        """
        Arduino setup() equivalent
        This function runs all the instructions once
        """
        # Initialize LEDs
        self.led.init_leds()
        
        # Init the pin for the serial button
        GPIO.setup(SERIAL_MODE_BUTTON_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Check if we should enter serial mode or not
        if GPIO.input(SERIAL_MODE_BUTTON_PORT) == GPIO.LOW:
            # Turn on blue LED
            self.led.digital_write(self.led.BLUE_LED_PIN, GPIO.HIGH)
            self.serial_menu.serial_function()
            # Turn off blue LED
            self.led.digital_write(self.led.BLUE_LED_PIN, GPIO.LOW)
            
        # Initialize port extenders (exact Arduino calls)
        InitPortExtender(MASTER)    # InitPortExtender(MASTER)
        InitPortExtender(SLAVE)     # InitPortExtender(SLAVE)
        
        # Initialize Ethernet
        if self.ethernet.eth_init() == "RETURN_ERROR":
            # If we enter this branch, there is a fault with the ethernet module
            # Turn Red LED on. This means a fatal fault has been detected.
            self.led.digital_write(self.led.RED_LED_PIN, GPIO.HIGH)
            while True:
                time.sleep(1)  # Infinite loop equivalent
                
        # Everything is ok with initialization turn green led on
        self.led.digital_write(self.led.GREEN_LED_PIN, GPIO.HIGH)
        
    def loop(self):
        """
        Arduino loop() equivalent
        This function runs in a loop every time. All instructions are run continuously
        """
        self.ethernet.eth_receive_telegram()
        
    def run(self):
        """Main execution function"""
        try:
            self.setup()
            print("CanMux initialized successfully. Starting main loop...")
            
            while True:
                self.loop()
                time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nShutting down CanMux...")
            self.cleanup()
            
    def cleanup(self):
        """Cleanup GPIO resources"""
        GPIO.cleanup()

# Arduino-like helper functions to maintain familiar syntax
def digitalWrite(pin, value):
    """Arduino digitalWrite equivalent"""
    GPIO.output(pin, value)

def digitalRead(pin):
    """Arduino digitalRead equivalent"""
    return GPIO.input(pin)

def pinMode(pin, mode):
    """Arduino pinMode equivalent"""
    if mode == "INPUT_PULLUP":
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    elif mode == "INPUT":
        GPIO.setup(pin, GPIO.IN)
    elif mode == "OUTPUT":
        GPIO.setup(pin, GPIO.OUT)

def delay(ms):
    """Arduino delay equivalent"""
    time.sleep(ms / 1000.0)

if __name__ == "__main__":
    # Initialize GPIO with BCM numbering (optimized for Pi 5)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    print("CAN MUX starting on Raspberry Pi...")
    
    # Create and run the main application
    can_mux = CanMux()
    can_mux.run()