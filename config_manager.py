#!/usr/bin/env python3
"""
Configuration Manager - Python port of EEPROM functionality
Handles network configuration storage and retrieval
"""

import json
import os
from pathlib import Path

class ConfigManager:
    """
    Manages network configuration - equivalent to Arduino EEPROM functionality
    Uses JSON file storage instead of EEPROM
    """
    
    def __init__(self, config_file="can_mux_config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            'mac': [0x60, 0x6D, 0x3C, 0xF1, 0x7E, 0xA0],
            'ip': [192, 168, 5, 11],
            'subnet_mask': [255, 255, 0, 0],
            'gateway': [192, 168, 0, 1],
            'dns': [192, 168, 0, 1]
        }
    
    def load_network_config(self):
        """
        Load network configuration from file
        Returns: Dictionary with network configuration
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Convert lists to proper format
                return {
                    'mac': ':'.join(f'{b:02x}' for b in config['mac']),
                    'ip': '.'.join(str(b) for b in config['ip']),
                    'subnet_mask': '.'.join(str(b) for b in config['subnet_mask']),
                    'gateway': '.'.join(str(b) for b in config['gateway']),
                    'dns': '.'.join(str(b) for b in config['dns'])
                }
            else:
                print("Configuration file not found, creating default configuration")
                self.save_network_config(self.default_config)
                return self.load_network_config()
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")
            return {
                'mac': ':'.join(f'{b:02x}' for b in self.default_config['mac']),
                'ip': '.'.join(str(b) for b in self.default_config['ip']),
                'subnet_mask': '.'.join(str(b) for b in self.default_config['subnet_mask']),
                'gateway': '.'.join(str(b) for b in self.default_config['gateway']),
                'dns': '.'.join(str(b) for b in self.default_config['dns'])
            }
    
    def save_network_config(self, config):
        """
        Save network configuration to file
        config: Dictionary with network configuration
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def read_eeprom_bytes(self, offset, count):
        """
        Arduino EEPROM.read() equivalent
        offset: Starting offset in EEPROM
        count: Number of bytes to read
        Returns: List of bytes
        """
        config = self.load_raw_config()
        
        # Map EEPROM offsets to configuration fields
        if offset == 0:  # IP address
            return config['ip'][:count]
        elif offset == 10:  # MAC address
            return config['mac'][:count]
        elif offset == 20:  # Subnet mask
            return config['subnet_mask'][:count]
        elif offset == 30:  # DNS
            return config['dns'][:count]
        elif offset == 40:  # Gateway
            return config['gateway'][:count]
        else:
            return [255] * count  # Return 0xFF for unknown offsets
    
    def write_eeprom_bytes(self, offset, data):
        """
        Arduino EEPROM.update() equivalent
        offset: Starting offset in EEPROM
        data: List of bytes to write
        """
        config = self.load_raw_config()
        
        # Map EEPROM offsets to configuration fields
        if offset == 0:  # IP address
            config['ip'] = data[:4]
        elif offset == 10:  # MAC address
            config['mac'] = data[:6]
        elif offset == 20:  # Subnet mask
            config['subnet_mask'] = data[:4]
        elif offset == 30:  # DNS
            config['dns'] = data[:4]
        elif offset == 40:  # Gateway
            config['gateway'] = data[:4]
        
        self.save_network_config(config)
    
    def load_raw_config(self):
        """Load raw configuration as byte arrays"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self.default_config.copy()
        except:
            return self.default_config.copy()
    
    def print_current_config(self):
        """Print current configuration - for debugging"""
        config = self.load_network_config()
        print("Current Network Configuration:")
        print(f"MAC: {config['mac']}")
        print(f"IP: {config['ip']}")
        print(f"Subnet Mask: {config['subnet_mask']}")
        print(f"Gateway: {config['gateway']}")
        print(f"DNS: {config['dns']}")

# Arduino EEPROM compatibility class
class EEPROM:
    """
    Arduino EEPROM library compatibility
    """
    _config_manager = ConfigManager()
    
    @classmethod
    def read(cls, address):
        """Read single byte from EEPROM - equivalent to EEPROM.read()"""
        # Determine which configuration field based on address ranges
        if 0 <= address <= 3:  # IP address
            config = cls._config_manager.load_raw_config()
            return config['ip'][address]
        elif 10 <= address <= 15:  # MAC address
            config = cls._config_manager.load_raw_config()
            return config['mac'][address - 10]
        elif 20 <= address <= 23:  # Subnet mask
            config = cls._config_manager.load_raw_config()
            return config['subnet_mask'][address - 20]
        elif 30 <= address <= 33:  # DNS
            config = cls._config_manager.load_raw_config()
            return config['dns'][address - 30]
        elif 40 <= address <= 43:  # Gateway
            config = cls._config_manager.load_raw_config()
            return config['gateway'][address - 40]
        else:
            return 255  # Return 0xFF for uninitialized EEPROM
    
    @classmethod
    def update(cls, address, value):
        """Update single byte in EEPROM - equivalent to EEPROM.update()"""
        config = cls._config_manager.load_raw_config()
        
        if 0 <= address <= 3:  # IP address
            config['ip'][address] = value
        elif 10 <= address <= 15:  # MAC address
            config['mac'][address - 10] = value
        elif 20 <= address <= 23:  # Subnet mask
            config['subnet_mask'][address - 20] = value
        elif 30 <= address <= 33:  # DNS
            config['dns'][address - 30] = value
        elif 40 <= address <= 43:  # Gateway
            config['gateway'][address - 40] = value
        
        cls._config_manager.save_network_config(config)

# Constants for EEPROM addresses (same as Arduino)
EEPROM_IP_ADDRESS_OFFSET = 0
EEPROM_MAC_ADDRESS_OFFSET = 10
EEPROM_SUBNET_MASK_ADDRESS_OFFSET = 20
EEPROM_DNS_ADDRESS_OFFSET = 30
EEPROM_GATEWAY_ADDRESS_OFFSET = 40

# Size constants
IP_MAX_BYTES = 4
MAC_MAX_BYTES = 6
SUBNET_MAX_BYTES = 4
GATEWAY_MAX_BYTES = 4
DNS_MAX_BYTES = 4