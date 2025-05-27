#!/usr/bin/env python3
"""
CAN MUX - Raspberry Pi Python Port cu Configuration Server
Main application file - equivalent to CanMux.ino cu server de configurare integrat
"""

import time
import threading
from gpio_pi5 import GPIO, digitalWrite, digitalRead, pinMode, delay
from ethernet_receive import EthernetReceive
from led_control import LEDControl
from serial_menu import SerialMenu
from port_extender import InitPortExtender, MASTER, SLAVE
from config_server import ConfigurationServer

# Arduino-like constants
SERIAL_MODE_BUTTON_PORT = 18  # BCM pin 18 (equivalent to A0)

class CanMux:
    def __init__(self):
        self.led = LEDControl()
        self.ethernet = EthernetReceive()
        self.serial_menu = SerialMenu()
        self.config_server = ConfigurationServer()  # Server pentru GUI
        
    def setup(self):
        """
        Arduino setup() equivalent
        This function runs all the instructions once
        """
        print("🚀 Initializing CAN MUX...")
        
        # Initialize LEDs
        self.led.init_leds()
        print("💡 LEDs initialized")
        
        # Init the pin for the serial button
        GPIO.setup(SERIAL_MODE_BUTTON_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print("🔘 Serial button configured")
        
        # Check if we should enter serial mode or not
        if GPIO.input(SERIAL_MODE_BUTTON_PORT) == GPIO.LOW:
            print("🔵 Serial mode button pressed - entering configuration mode")
            # Turn on blue LED
            self.led.digital_write(self.led.BLUE_LED_PIN, GPIO.HIGH)
            self.serial_menu.serial_function()
            # Turn off blue LED
            self.led.digital_write(self.led.BLUE_LED_PIN, GPIO.LOW)
            
        # Initialize port extenders (exact Arduino calls)
        print("🔌 Initializing port extenders...")
        InitPortExtender(MASTER)    # InitPortExtender(MASTER)
        InitPortExtender(SLAVE)     # InitPortExtender(SLAVE)
        print("✅ Port extenders initialized")
        
        # Start Configuration Server în thread separat ÎNAINTE de ethernet
        print("🔧 Starting configuration server...")
        self.start_config_server()
        
        # Initialize Ethernet
        print("🌐 Initializing Ethernet...")
        if self.ethernet.eth_init() == "RETURN_ERROR":
            # If we enter this branch, there is a fault with the ethernet module
            # Turn Red LED on. This means a fatal fault has been detected.
            self.led.digital_write(self.led.RED_LED_PIN, GPIO.HIGH)
            print("❌ FATAL ERROR: Ethernet initialization failed!")
            print("🔴 Red LED ON - check Ethernet connection")
            while True:
                time.sleep(1)  # Infinite loop equivalent
                
        print("✅ Ethernet initialized successfully")
                
        # Everything is ok with initialization turn green led on
        self.led.digital_write(self.led.GREEN_LED_PIN, GPIO.HIGH)
        print("🟢 All systems initialized - Green LED ON")
        print("")
        print("📋 CAN MUX Status:")
        print("   🔌 Main TCP Server: Port 3363 (for Hercules)")
        print("   🔧 Config Server: Port 3364 (for GUI)")
        print("   💡 Status: Green LED (ready)")
        print("   🔘 Serial Config: Available via button")
        print("")
        
    def start_config_server(self):
        """Pornește serverul de configurare într-un thread separat"""
        try:
            config_thread = threading.Thread(
                target=self.config_server.start_server,
                daemon=True,
                name="ConfigServer"
            )
            config_thread.start()
            print("✅ Configuration server started in background")
            time.sleep(0.5)  # Give server time to start
        except Exception as e:
            print(f"⚠️  WARNING: Could not start configuration server: {e}")
            print("   GUI configuration will not be available")
            print("   You can still use serial configuration mode")
        
    def loop(self):
        """
        Arduino loop() equivalent
        This function runs in a loop every time. All instructions are run continuously
        """
        self.ethernet.eth_receive_telegram()
        
    def run(self):
        """Main execution function"""
        try:
            print("=" * 60)
            print("🚀 CAN MUX - Raspberry Pi Python Port")
            print("=" * 60)
            print("📡 Network Configuration Tool for CAN Multiplexer")
            print("🍓 Optimized for Raspberry Pi 5")
            print("🔗 Ethernet connection ready")
            print("")
            
            self.setup()
            
            print("🔄 Starting main communication loop...")
            print("   ⏹️  Press Ctrl+C to stop")
            print("   📨 Waiting for Hercules telegrams on port 3363...")
            print("   🖥️  GUI can connect on port 3364 for configuration")
            print("")
            
            # Main loop pentru procesarea telegramelor
            while True:
                self.loop()
                time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("🛑 Shutdown initiated by user (Ctrl+C)")
            print("🧹 Cleaning up resources...")
            self.cleanup()
            print("✅ CAN MUX stopped successfully")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("🧹 Cleaning up resources...")
            self.cleanup()
            print("❌ CAN MUX stopped due to error")
            
    def cleanup(self):
        """Cleanup GPIO resources and servers"""
        print("   🔧 Stopping configuration server...")
        try:
            self.config_server.stop_server()
            print("   ✅ Configuration server stopped")
        except Exception as e:
            print(f"   ⚠️  Config server cleanup warning: {e}")
            
        print("   🌐 Stopping ethernet server...")
        try:
            self.ethernet.cleanup()
            print("   ✅ Ethernet server stopped")
        except Exception as e:
            print(f"   ⚠️  Ethernet cleanup warning: {e}")
            
        print("   🔌 Cleaning up GPIO...")
        try:
            # Turn off all LEDs
            self.led.digital_write(self.led.RED_LED_PIN, False)
            self.led.digital_write(self.led.GREEN_LED_PIN, False)
            self.led.digital_write(self.led.BLUE_LED_PIN, False)
            GPIO.cleanup()
            print("   ✅ GPIO cleaned up")
        except Exception as e:
            print(f"   ⚠️  GPIO cleanup warning: {e}")

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
    
    # Create and run the main application
    can_mux = CanMux()
    can_mux.run()