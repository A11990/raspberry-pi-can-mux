#!/usr/bin/env python3
"""
Serial Menu module - Python port of SerialMenu.cpp
Handles configuration menu via console input
"""

import time
from config_manager import ConfigManager, EEPROM
from config_manager import (
    EEPROM_IP_ADDRESS_OFFSET, EEPROM_MAC_ADDRESS_OFFSET,
    EEPROM_SUBNET_MASK_ADDRESS_OFFSET, EEPROM_DNS_ADDRESS_OFFSET,
    EEPROM_GATEWAY_ADDRESS_OFFSET, IP_MAX_BYTES, MAC_MAX_BYTES,
    SUBNET_MAX_BYTES, GATEWAY_MAX_BYTES, DNS_MAX_BYTES
)

class SerialMenu:
    """
    Serial configuration menu - equivalent to Arduino SerialMenu functionality
    """
    
    # Menu options (same as Arduino)
    CHANGE_MAC = '1'
    CHANGE_IP = '2'
    CHANGE_SUBNET_MASK = '3'
    CHANGE_GATEWAY = '4'
    CHANGE_DNS = '5'
    EXIT = '0'
    
    # Base constants
    BASE_10 = 10
    BASE_16 = 16
    
    # Firmware version
    FW_VERSION_MAJOR = 1
    FW_VERSION_MINOR = 4
    ETH_PORT = 3363
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.incoming_byte = 0
    
    def serial_function(self):
        """
        Main serial function - equivalent to SerialFunction()
        Handles the serial configuration menu
        """
        print("Serial mode activated!")
        
        # First draw of the main menu
        self.serial_main_menu()
        
        exit_menu = False
        
        while not exit_menu:
            try:
                # Get user input
                user_input = input().strip()
                if len(user_input) > 0:
                    self.incoming_byte = user_input[0]
                else:
                    continue
                
                if self.incoming_byte == self.CHANGE_MAC:
                    self._change_mac()
                elif self.incoming_byte == self.CHANGE_IP:
                    self._change_ip()
                elif self.incoming_byte == self.CHANGE_SUBNET_MASK:
                    self._change_subnet_mask()
                elif self.incoming_byte == self.CHANGE_GATEWAY:
                    self._change_gateway()
                elif self.incoming_byte == self.CHANGE_DNS:
                    self._change_dns()
                elif self.incoming_byte == self.EXIT:
                    exit_menu = True
                    print("\nExiting from serial mode in 5 seconds...")
                    time.sleep(5)
                    print("-------------------------------------------------------------------------------------")
                    print("Serial session has ended.")
                else:
                    print("\nOption is invalid")
                    print("Returning to the Main Menu in 5 seconds...")
                    time.sleep(5)
                    print("-------------------------------------------------------------------------------------")
                    self.serial_main_menu()
                    
            except KeyboardInterrupt:
                print("\nExiting serial mode...")
                break
            except Exception as e:
                print(f"Error in serial menu: {e}")
    
    def _change_mac(self):
        """Change MAC address"""
        print("\nPlease enter the new MAC. Example: DE.CD.AE.0F.FE.ED")
        try:
            mac_input = input().strip()
            mac_bytes = self.parse_bytes(mac_input, '.', MAC_MAX_BYTES, self.BASE_16)
            
            # Write the new MAC into EEPROM
            for i in range(MAC_MAX_BYTES):
                EEPROM.update(EEPROM_MAC_ADDRESS_OFFSET + i, mac_bytes[i])
            
            print("The new MAC is: ", end="")
            self.serial_print_mac()
            print("\nReturning to the Main Menu in 5 seconds...")
            time.sleep(5)
            print("-------------------------------------------------------------------------------------")
            self.serial_main_menu()
            
        except Exception as e:
            print(f"Error changing MAC: {e}")
            self.serial_main_menu()
    
    def _change_ip(self):
        """Change IP address"""
        print("\nPlease enter the new IP. Example: 192.168.1.10")
        try:
            ip_input = input().strip()
            ip_bytes = self.parse_bytes(ip_input, '.', IP_MAX_BYTES, self.BASE_10)
            
            # Write the new IP into EEPROM
            for i in range(IP_MAX_BYTES):
                EEPROM.update(EEPROM_IP_ADDRESS_OFFSET + i, ip_bytes[i])
            
            # Display new IP
            new_ip = f"{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+3)}"
            print(f"The new IP is: {new_ip}")
            print("\nReturning to the Main Menu in 5 seconds...")
            time.sleep(5)
            print("-------------------------------------------------------------------------------------")
            self.serial_main_menu()
            
        except Exception as e:
            print(f"Error changing IP: {e}")
            self.serial_main_menu()
    
    def _change_subnet_mask(self):
        """Change subnet mask"""
        print("\nPlease enter the new Subnet Mask. Example: 255.255.0.0")
        try:
            subnet_input = input().strip()
            subnet_bytes = self.parse_bytes(subnet_input, '.', SUBNET_MAX_BYTES, self.BASE_10)
            
            # Write the new subnet mask into EEPROM
            for i in range(SUBNET_MAX_BYTES):
                EEPROM.update(EEPROM_SUBNET_MASK_ADDRESS_OFFSET + i, subnet_bytes[i])
            
            # Display new subnet mask
            new_subnet = f"{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+3)}"
            print(f"The new Subnet mask is: {new_subnet}")
            print("\nReturning to the Main Menu in 5 seconds...")
            time.sleep(5)
            print("-------------------------------------------------------------------------------------")
            self.serial_main_menu()
            
        except Exception as e:
            print(f"Error changing subnet mask: {e}")
            self.serial_main_menu()
    
    def _change_gateway(self):
        """Change gateway"""
        print("\nPlease enter the new Gateway. Example: 192.168.1.0")
        try:
            gateway_input = input().strip()
            gateway_bytes = self.parse_bytes(gateway_input, '.', GATEWAY_MAX_BYTES, self.BASE_10)
            
            # Write the new gateway into EEPROM
            for i in range(GATEWAY_MAX_BYTES):
                EEPROM.update(EEPROM_GATEWAY_ADDRESS_OFFSET + i, gateway_bytes[i])
            
            # Display new gateway
            new_gateway = f"{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+3)}"
            print(f"The new Gateway is: {new_gateway}")
            print("\nReturning to the Main Menu in 5 seconds...")
            time.sleep(5)
            print("-------------------------------------------------------------------------------------")
            self.serial_main_menu()
            
        except Exception as e:
            print(f"Error changing gateway: {e}")
            self.serial_main_menu()
    
    def _change_dns(self):
        """Change DNS"""
        print("\nPlease enter the new DNS. Example: 192.168.1.0")
        try:
            dns_input = input().strip()
            dns_bytes = self.parse_bytes(dns_input, '.', DNS_MAX_BYTES, self.BASE_10)
            
            # Write the new DNS into EEPROM
            for i in range(DNS_MAX_BYTES):
                EEPROM.update(EEPROM_DNS_ADDRESS_OFFSET + i, dns_bytes[i])
            
            # Display new DNS
            new_dns = f"{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+3)}"
            print(f"The new DNS is: {new_dns}")
            print("\nReturning to the Main Menu in 5 seconds...")
            time.sleep(5)
            print("-------------------------------------------------------------------------------------")
            self.serial_main_menu()
            
        except Exception as e:
            print(f"Error changing DNS: {e}")
            self.serial_main_menu()
    
    def parse_bytes(self, input_str, separator, max_bytes, base):
        """
        Parse bytes from string - equivalent to ParseBytes()
        input_str: Input string to parse
        separator: Character separator
        max_bytes: Maximum number of bytes
        base: Number base (10 or 16)
        Returns: List of bytes
        """
        try:
            parts = input_str.split(separator)
            bytes_list = []
            
            for i in range(min(len(parts), max_bytes)):
                if base == 16:
                    byte_val = int(parts[i], 16)
                else:
                    byte_val = int(parts[i])
                
                # Ensure byte value is in valid range
                if 0 <= byte_val <= 255:
                    bytes_list.append(byte_val)
                else:
                    raise ValueError(f"Byte value {byte_val} out of range (0-255)")
            
            return bytes_list
            
        except Exception as e:
            print(f"Error parsing bytes: {e}")
            raise
    
    def serial_print_mac(self):
        """
        Print MAC address - equivalent to SerialPrintMAC()
        """
        mac_parts = []
        for i in range(MAC_MAX_BYTES):
            byte_val = EEPROM.read(EEPROM_MAC_ADDRESS_OFFSET + i)
            mac_parts.append(f"{byte_val:02X}")
        
        print(".".join(mac_parts))
    
    def serial_main_menu(self):
        """
        Print main menu - equivalent to SerialMainMenu()
        """
        print("Welcome to the CAN MUX serial menu!")
        print("")
        print(f"Firmware Version: {self.FW_VERSION_MAJOR}.{self.FW_VERSION_MINOR}")
        print("")
        print("Current settings are:")
        
        # Print MAC
        print("MAC: ", end="")
        self.serial_print_mac()
        
        # Print IP
        ip_str = f"{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_IP_ADDRESS_OFFSET+3)}"
        print(f"IP: {ip_str}")
        
        # Print Port
        print(f"Port: {self.ETH_PORT} - this is fixed and cannot be changed!")
        
        # Print Subnet Mask
        subnet_str = f"{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_SUBNET_MASK_ADDRESS_OFFSET+3)}"
        print(f"Subnet Mask: {subnet_str}")
        
        # Print Gateway
        gateway_str = f"{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_GATEWAY_ADDRESS_OFFSET+3)}"
        print(f"Gateway: {gateway_str}")
        
        # Print DNS
        dns_str = f"{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+0)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+1)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+2)}.{EEPROM.read(EEPROM_DNS_ADDRESS_OFFSET+3)}"
        print(f"DNS: {dns_str}")
        
        print("")
        print("")
        print("Select one of the following options by entering appropriate number:")
        print("1 - To change the MAC")
        print("2 - To change the IP")
        print("3 - To change the Subnet Mask")
        print("4 - To change the Gateway")
        print("5 - To change the DNS")
        print("0 - EXIT - Return to normal operation of the device")
        print("-------------------------------------------------------------------------------------")
        print("")
        print("Please type in your option... ")