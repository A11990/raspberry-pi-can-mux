#!/usr/bin/env python3
"""
GPIO wrapper optimized for Raspberry Pi 5
Provides compatibility layer between lgpio (Pi 5) and RPi.GPIO (older Pi)
"""

import sys
import platform

# Try to detect Raspberry Pi 5
def is_raspberry_pi_5():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            model = f.read()
            return 'Raspberry Pi 5' in model
    except:
        return False

# Initialize GPIO library based on Pi version
PI5_DETECTED = is_raspberry_pi_5()

if PI5_DETECTED:
    print("Raspberry Pi 5 detected - using lgpio library")
    try:
        import lgpio
        GPIO_LIB = 'lgpio'
        # Open GPIO chip
        gpio_chip = lgpio.gpiochip_open(0)
    except ImportError:
        print("lgpio not available, falling back to RPi.GPIO")
        import RPi.GPIO as GPIO
        GPIO_LIB = 'RPi.GPIO'
else:
    print("Using RPi.GPIO library")
    import RPi.GPIO as GPIO
    GPIO_LIB = 'RPi.GPIO'

class GPIO_Pi5:
    """
    GPIO wrapper class that works on both Pi 5 (lgpio) and older Pi (RPi.GPIO)
    Maintains Arduino-like interface
    """
    
    # Constants
    HIGH = 1
    LOW = 0
    OUT = 1
    IN = 0
    PUD_UP = 1
    PUD_DOWN = 2
    PUD_OFF = 0
    BCM = 11
    
    @staticmethod
    def setmode(mode):
        """Set GPIO numbering mode"""
        if GPIO_LIB == 'RPi.GPIO':
            GPIO.setmode(GPIO.BCM if mode == GPIO_Pi5.BCM else GPIO.BOARD)
    
    @staticmethod
    def setwarnings(state):
        """Enable/disable warnings"""
        if GPIO_LIB == 'RPi.GPIO':
            GPIO.setwarnings(state)
    
    @staticmethod
    def setup(pin, mode, pull_up_down=PUD_OFF):
        """Setup GPIO pin"""
        if GPIO_LIB == 'lgpio':
            if mode == GPIO_Pi5.OUT:
                lgpio.gpio_claim_output(gpio_chip, pin)
            else:  # INPUT
                if pull_up_down == GPIO_Pi5.PUD_UP:
                    lgpio.gpio_claim_input(gpio_chip, pin, lgpio.SET_PULL_UP)
                elif pull_up_down == GPIO_Pi5.PUD_DOWN:
                    lgpio.gpio_claim_input(gpio_chip, pin, lgpio.SET_PULL_DOWN)
                else:
                    lgpio.gpio_claim_input(gpio_chip, pin)
        else:  # RPi.GPIO
            pud_map = {
                GPIO_Pi5.PUD_OFF: GPIO.PUD_OFF,
                GPIO_Pi5.PUD_UP: GPIO.PUD_UP,
                GPIO_Pi5.PUD_DOWN: GPIO.PUD_DOWN
            }
            mode_map = {GPIO_Pi5.OUT: GPIO.OUT, GPIO_Pi5.IN: GPIO.IN}
            GPIO.setup(pin, mode_map[mode], pull_up_down=pud_map[pull_up_down])
    
    @staticmethod
    def output(pin, value):
        """Set GPIO output value"""
        if GPIO_LIB == 'lgpio':
            lgpio.gpio_write(gpio_chip, pin, value)
        else:
            GPIO.output(pin, value)
    
    @staticmethod
    def input(pin):
        """Read GPIO input value"""
        if GPIO_LIB == 'lgpio':
            return lgpio.gpio_read(gpio_chip, pin)
        else:
            return GPIO.input(pin)
    
    @staticmethod
    def cleanup():
        """Cleanup GPIO resources"""
        if GPIO_LIB == 'lgpio':
            lgpio.gpiochip_close(gpio_chip)
        else:
            GPIO.cleanup()

# Arduino-like helper functions using the wrapper
def digitalWrite(pin, value):
    """Arduino digitalWrite equivalent"""
    GPIO_Pi5.output(pin, GPIO_Pi5.HIGH if value else GPIO_Pi5.LOW)

def digitalRead(pin):
    """Arduino digitalRead equivalent"""
    return GPIO_Pi5.input(pin) == GPIO_Pi5.HIGH

def pinMode(pin, mode):
    """Arduino pinMode equivalent"""
    if mode == "OUTPUT":
        GPIO_Pi5.setup(pin, GPIO_Pi5.OUT)
    elif mode == "INPUT":
        GPIO_Pi5.setup(pin, GPIO_Pi5.IN)
    elif mode == "INPUT_PULLUP":
        GPIO_Pi5.setup(pin, GPIO_Pi5.IN, GPIO_Pi5.PUD_UP)

def delay(ms):
    """Arduino delay equivalent"""
    import time
    time.sleep(ms / 1000.0)

# Export the wrapper as GPIO for compatibility
GPIO = GPIO_Pi5

print(f"GPIO library initialized: {GPIO_LIB}")
if PI5_DETECTED:
    print("Optimized for Raspberry Pi 5 performance")