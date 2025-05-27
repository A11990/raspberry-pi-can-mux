#!/usr/bin/env python3
"""
CAN MUX Configuration Server
Server care rulează pe Raspberry Pi și permite configurarea remotă
Portul 3364 pentru configurare (diferit de portul principal 3363)
"""

import socket
import threading
import json
import time
from config_manager import ConfigManager, EEPROM
from config_manager import (
    EEPROM_IP_ADDRESS_OFFSET, EEPROM_MAC_ADDRESS_OFFSET,
    EEPROM_SUBNET_MASK_ADDRESS_OFFSET, EEPROM_DNS_ADDRESS_OFFSET,
    EEPROM_GATEWAY_ADDRESS_OFFSET, IP_MAX_BYTES, MAC_MAX_BYTES,
    SUBNET_MAX_BYTES, GATEWAY_MAX_BYTES, DNS_MAX_BYTES
)

class ConfigurationServer:
    def __init__(self, port=3364):
        self.port = port
        self.config_manager = ConfigManager()
        self.server_socket = None
        self.running = False
        
        # Firmware version
        self.FW_VERSION_MAJOR = 1
        self.FW_VERSION_MINOR = 4
        
    def start_server(self):
        """Pornește serverul de configurare"""
        try:
            # Încarcă configurația pentru a afla IP-ul
            config = self.config_manager.load_network_config()
            
            # Creează socket-ul server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((config['ip'], self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            print(f"🔧 Configuration server started on {config['ip']}:{self.port}")
            print(f"📡 Ready for GUI connections...")
            
            # Loop principal pentru acceptarea conexiunilor
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"🖥️  GUI client connected from {client_address}")
                    
                    # Procesează clientul într-un thread separat
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Server error: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to start configuration server: {e}")
            return False
            
        return True
        
    def handle_client(self, client_socket, client_address):
        """Procesează un client conectat"""
        try:
            buffer = b""
            
            while self.running:
                # Primește date
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                buffer += data
                
                # Procesează mesajele complete (terminate cu \n)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line:
                        self.process_message(line.decode('utf-8'), client_socket)
                        
        except Exception as e:
            print(f"❌ Client handling error for {client_address}: {e}")
        finally:
            print(f"🔌 GUI client {client_address} disconnected")
            client_socket.close()
            
    def process_message(self, message, client_socket):
        """Procesează un mesaj primit de la client"""
        try:
            # Parse JSON message
            request = json.loads(message)
            command = request.get('command')
            data = request.get('data', {})
            
            print(f"📨 Received command: {command}")
            
            # Procesează comanda
            if command == "get_config":
                response = self.get_current_config()
            elif command == "update_config":
                response = self.update_single_config(data)
            elif command == "update_all_config":
                response = self.update_all_config(data)
            elif command == "get_firmware":
                response = self.get_firmware_info()
            else:
                response = {
                    "status": "error",
                    "message": f"Unknown command: {command}"
                }
                
            # Trimite răspunsul
            response_json = json.dumps(response) + '\n'
            client_socket.send(response_json.encode())
            
            print(f"📤 Sent response: {response['status']}")
            
        except json.JSONDecodeError:
            error_response = {
                "status": "error",
                "message": "Invalid JSON message"
            }
            client_socket.send((json.dumps(error_response) + '\n').encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e)
            }
            client_socket.send((json.dumps(error_response) + '\n').encode())
            print(f"❌ Error processing message: {e}")
            
    def get_current_config(self):
        """Obține configurația curentă"""
        try:
            # Citește configurația formatată
            config = self.config_manager.load_network_config()
            
            # Adaugă informații despre firmware
            config['firmware'] = f"{self.FW_VERSION_MAJOR}.{self.FW_VERSION_MINOR}"
            
            return {
                "status": "success",
                "data": config
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read configuration: {str(e)}"
            }
            
    def get_firmware_info(self):
        """Obține informații despre firmware"""
        return {
            "status": "success",
            "data": {
                "major": self.FW_VERSION_MAJOR,
                "minor": self.FW_VERSION_MINOR,
                "version": f"{self.FW_VERSION_MAJOR}.{self.FW_VERSION_MINOR}"
            }
        }
        
    def update_single_config(self, data):
        """Update o singură configurație"""
        try:
            if len(data) != 1:
                return {
                    "status": "error",
                    "message": "Expected exactly one configuration parameter"
                }
                
            config_type, value = next(iter(data.items()))
            
            # Validează și convertește valorile
            if config_type == "mac":
                mac_bytes = self.parse_mac(value)
                # Scrie MAC în EEPROM
                for i in range(MAC_MAX_BYTES):
                    EEPROM.update(EEPROM_MAC_ADDRESS_OFFSET + i, mac_bytes[i])
                    
            elif config_type == "ip":
                ip_bytes = self.parse_ip(value)
                # Scrie IP în EEPROM
                for i in range(IP_MAX_BYTES):
                    EEPROM.update(EEPROM_IP_ADDRESS_OFFSET + i, ip_bytes[i])
                    
            elif config_type == "subnet_mask":
                subnet_bytes = self.parse_ip(value)
                # Scrie Subnet Mask în EEPROM
                for i in range(SUBNET_MAX_BYTES):
                    EEPROM.update(EEPROM_SUBNET_MASK_ADDRESS_OFFSET + i, subnet_bytes[i])
                    
            elif config_type == "gateway":
                gateway_bytes = self.parse_ip(value)
                # Scrie Gateway în EEPROM
                for i in range(GATEWAY_MAX_BYTES):
                    EEPROM.update(EEPROM_GATEWAY_ADDRESS_OFFSET + i, gateway_bytes[i])
                    
            elif config_type == "dns":
                dns_bytes = self.parse_ip(value)
                # Scrie DNS în EEPROM
                for i in range(DNS_MAX_BYTES):
                    EEPROM.update(EEPROM_DNS_ADDRESS_OFFSET + i, dns_bytes[i])
                    
            else:
                return {
                    "status": "error",
                    "message": f"Unknown configuration type: {config_type}"
                }
                
            print(f"✅ Updated {config_type}: {value}")
            
            return {
                "status": "success",
                "message": f"{config_type} updated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update {config_type}: {str(e)}"
            }
            
    def update_all_config(self, data):
        """Update toate configurațiile specificate"""
        try:
            updated_items = []
            
            for config_type, value in data.items():
                try:
                    # Validează și convertește valorile
                    if config_type == "mac":
                        mac_bytes = self.parse_mac(value)
                        # Scrie MAC în EEPROM
                        for i in range(MAC_MAX_BYTES):
                            EEPROM.update(EEPROM_MAC_ADDRESS_OFFSET + i, mac_bytes[i])
                            
                    elif config_type == "ip":
                        ip_bytes = self.parse_ip(value)
                        # Scrie IP în EEPROM
                        for i in range(IP_MAX_BYTES):
                            EEPROM.update(EEPROM_IP_ADDRESS_OFFSET + i, ip_bytes[i])
                            
                    elif config_type == "subnet_mask":
                        subnet_bytes = self.parse_ip(value)
                        # Scrie Subnet Mask în EEPROM
                        for i in range(SUBNET_MAX_BYTES):
                            EEPROM.update(EEPROM_SUBNET_MASK_ADDRESS_OFFSET + i, subnet_bytes[i])
                            
                    elif config_type == "gateway":
                        gateway_bytes = self.parse_ip(value)
                        # Scrie Gateway în EEPROM
                        for i in range(GATEWAY_MAX_BYTES):
                            EEPROM.update(EEPROM_GATEWAY_ADDRESS_OFFSET + i, gateway_bytes[i])
                            
                    elif config_type == "dns":
                        dns_bytes = self.parse_ip(value)
                        # Scrie DNS în EEPROM
                        for i in range(DNS_MAX_BYTES):
                            EEPROM.update(EEPROM_DNS_ADDRESS_OFFSET + i, dns_bytes[i])
                            
                    else:
                        print(f"⚠️  Unknown configuration type: {config_type}")
                        continue
                        
                    updated_items.append(config_type)
                    print(f"✅ Updated {config_type}: {value}")
                    
                except Exception as e:
                    print(f"❌ Failed to update {config_type}: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to update {config_type}: {str(e)}"
                    }
                    
            if not updated_items:
                return {
                    "status": "error",
                    "message": "No valid configuration items provided"
                }
                
            return {
                "status": "success",
                "message": f"Updated {len(updated_items)} configuration items: {', '.join(updated_items)}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update configuration: {str(e)}"
            }
            
    def parse_mac(self, mac_str):
        """Parse MAC address din string"""
        try:
            # Remove spaces and convert to uppercase
            mac_str = mac_str.replace(' ', '').upper()
            
            # Split by dots or colons
            if '.' in mac_str:
                parts = mac_str.split('.')
            elif ':' in mac_str:
                parts = mac_str.split(':')
            elif '-' in mac_str:
                parts = mac_str.split('-')
            else:
                # Try to parse as continuous string
                if len(mac_str) == 12:
                    parts = [mac_str[i:i+2] for i in range(0, 12, 2)]
                else:
                    raise ValueError("Invalid MAC format")
                    
            if len(parts) != 6:
                raise ValueError("MAC address must have 6 parts")
                
            mac_bytes = []
            for part in parts:
                byte_val = int(part, 16)
                if not 0 <= byte_val <= 255:
                    raise ValueError(f"MAC byte {part} out of range")
                mac_bytes.append(byte_val)
                
            return mac_bytes
            
        except Exception as e:
            raise ValueError(f"Invalid MAC address format: {str(e)}")
            
    def parse_ip(self, ip_str):
        """Parse IP address din string"""
        try:
            parts = ip_str.split('.')
            if len(parts) != 4:
                raise ValueError("IP address must have 4 parts")
                
            ip_bytes = []
            for part in parts:
                byte_val = int(part)
                if not 0 <= byte_val <= 255:
                    raise ValueError(f"IP octet {part} out of range (0-255)")
                ip_bytes.append(byte_val)
                
            return ip_bytes
            
        except Exception as e:
            raise ValueError(f"Invalid IP address format: {str(e)}")
            
    def stop_server(self):
        """Oprește serverul"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("🔧 Configuration server stopped")

def main():
    """Funcția principală pentru rularea serverului"""
    print("🚀 Starting CAN MUX Configuration Server...")
    
    server = ConfigurationServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Stopping configuration server...")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()