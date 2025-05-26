#!/usr/bin/env python3
"""
LED Control module - Python port of LED.cpp
Handles RGB LED control - Optimized for Raspberry Pi 5
"""

from gpio_pi5 import GPIO

class LEDControl:
    # LED pin definitions (adjust these to your actual GPIO pins)
    RED_LED_PIN = 4      # GPIO 4
    GREEN_LED_PIN = 8    # GPIO 8  
    BLUE_LED_PIN = 7     # GPIO 7
    
    def __init__(self):
        pass
    
    def init_leds(self):
        """
        Initialize LEDs - equivalent to InitLEDs()
        """
        # Set pins as outputs
        GPIO.setup(self.RED_LED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_LED_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_LED_PIN, GPIO.OUT)
        
        # Turn all LEDs off initially
        GPIO.output(self.RED_LED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_LED_PIN, GPIO.LOW)
        
        print("LEDs initialized")
    
    def digital_write(self, pin, value):
        """
        Arduino-style digitalWrite for LEDs
        """
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
    
    def set_color_red(self):
        """Set LED color to red"""
        self.digital_write(self.RED_LED_PIN, True)
        self.digital_write(self.GREEN_LED_PIN, False)
        self.digital_write(self.BLUE_LED_PIN, False)
    
    def set_color_green(self):
        """Set LED color to green"""
        self.digital_write(self.RED_LED_PIN, False)
        self.digital_write(self.GREEN_LED_PIN, True)
        self.digital_write(self.BLUE_LED_PIN, False)
    
    def set_color_blue(self):
        """Set LED color to blue"""
        self.digital_write(self.RED_LED_PIN, False)
        self.digital_write(self.GREEN_LED_PIN, False)
        self.digital_write(self.BLUE_LED_PIN, True)
    
    def set_color_yellow(self):
        """Set LED color to yellow (red + green)"""
        self.digital_write(self.RED_LED_PIN, True)
        self.digital_write(self.GREEN_LED_PIN, True)
        self.digital_write(self.BLUE_LED_PIN, False)
    
    def set_color_purple(self):
        """Set LED color to purple (red + blue)"""
        self.digital_write(self.RED_LED_PIN, True)
        self.digital_write(self.GREEN_LED_PIN, False)
        self.digital_write(self.BLUE_LED_PIN, True)
    
    def set_color_cyan(self):
        """Set LED color to cyan (green + blue)"""
        self.digital_write(self.RED_LED_PIN, False)
        self.digital_write(self.GREEN_LED_PIN, True)
        self.digital_write(self.BLUE_LED_PIN, True)
    
    def set_color_white(self):
        """Set LED color to white (all on)"""
        self.digital_write(self.RED_LED_PIN, True)
        self.digital_write(self.GREEN_LED_PIN, True)
        self.digital_write(self.BLUE_LED_PIN, True)
    
    def set_color_off(self):
        """Turn all LEDs off"""
        self.digital_write(self.RED_LED_PIN, False)
        self.digital_write(self.GREEN_LED_PIN, False)
        self.digital_write(self.BLUE_LED_PIN, False)

# Arduino-like helper functions for backward compatibility
def digitalWrite(pin, value):
    """Arduino digitalWrite equivalent"""
    GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)

def pinMode(pin, mode):
    """Arduino pinMode equivalent"""
    if mode == "OUTPUT":
        GPIO.setup(pin, GPIO.OUT)
    elif mode == "INPUT":
        GPIO.setup(pin, GPIO.IN)
    elif mode == "INPUT_PULLUP":
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)