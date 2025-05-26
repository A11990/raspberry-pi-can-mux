#!/usr/bin/env python3
"""
EthernetReceive module - Python port of EthernetReceive.cpp
Handles Ethernet communication and telegram processing
"""

import socket
import threading
import struct
import time
from zlib import crc32
from led_control import LEDControl
from port_extender import InitPortExtender, PortExtenderSetPin, PortExtenderMaster, PortExtenderSlave, MASTER, SLAVE
from FaBoGPIO_PCAL6408_Modified import PCAL6408_OUTPUT_REG
from config_manager import ConfigManager

class EthernetReceive:
    # Constants (same as Arduino)
    SELECT_CHANNEL = 0x01
    GET_CHANNEL_STATUS = 0x02
    GET_FIRMWARE_VERSION = 0x03
    ERROR_CHECKSUM_NOK = 0x01
    ERROR_PAYLOAD_NOK = 0x02
    ERROR_TELEGRAM_ID_NOK = 0x03
    ERROR_SLAVE_NOT_FOUND = 0x04
    ERROR_MASTER_NOT_FOUND = 0x05
    ETH_PORT = 3363
    RETURN_SUCCESS = 0
    RETURN_ERROR = 1
    
    # Firmware version constants
    FW_VERSION_MAJOR = 1
    FW_VERSION_MINOR = 4
    
    def __init__(self):
        self.led = LEDControl()
        self.config = ConfigManager()
        
        # Variables equivalent to Arduino globals
        self.eth_input_byte = 0
        self.eth_data_array = [0] * 10
        self.crc_location = 0
        self.index = 0
        self.checksum = 0
        
        # Socket server
        self.server_socket = None
        self.client_socket = None
        self.server_thread = None
        self.running = False
        
    def eth_init(self):
        """
        Initialize Ethernet module - equivalent to EthInit()
        Returns: RETURN_SUCCESS or RETURN_ERROR
        """
        try:
            # Load network configuration
            config = self.config.load_network_config()
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((config['ip'], self.ETH_PORT))
            self.server_socket.listen(1)
            
            print(f"Ethernet server started on {config['ip']}:{self.ETH_PORT}")
            
            # Start server in separate thread
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            return "RETURN_SUCCESS"
            
        except Exception as e:
            print(f"Ethernet initialization error: {e}")
            return "RETURN_ERROR"
    
    def _server_loop(self):
        """Server loop running in separate thread"""
        while self.running:
            try:
                print("Waiting for client connection...")
                self.client_socket, client_address = self.server_socket.accept()
                print(f"Client connected from {client_address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(self.client_socket,), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Server loop error: {e}")
                    time.sleep(1)
    
    def _handle_client(self, client_socket):
        """Handle individual client connection"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                # Process received data byte by byte (Arduino style)
                for byte_val in data:
                    self._process_byte(byte_val, client_socket)
                    
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            client_socket.close()
    
    def _process_byte(self, byte_val, client_socket):
        """Process single byte - equivalent to Arduino byte processing logic"""
        self.eth_input_byte = byte_val
        
        # If this is the first byte, determine telegram length
        if self.index == 0:
            expected_length = self.check_length()
            # Note: In real implementation, you might want to validate expected length
            
        # Put the byte into the data array
        self.eth_data_array[self.index] = self.eth_input_byte
        self.index += 1
        
        # If all bytes have been received - end of telegram
        if self.index == self.crc_location:
            self._process_complete_telegram(client_socket)
            # Reset for next telegram
            self.index = 0
            self.crc_location = 0
            self.init_array()
    
    def _process_complete_telegram(self, client_socket):
        """Process complete telegram - equivalent to Arduino telegram processing"""
        # Load checksum data (last 4 bytes)
        received_checksum = (
            self.eth_data_array[self.crc_location - 1] |
            (self.eth_data_array[self.crc_location - 2] << 8) |
            (self.eth_data_array[self.crc_location - 3] << 16) |
            (self.eth_data_array[self.crc_location - 4] << 24)
        )
        
        # Calculate checksum
        self.check_sum()
        
        # Check if checksum is OK
        if self.checksum == received_checksum:
            if self.eth_data_array[0] == self.SELECT_CHANNEL:
                self.select_channel_telegram(client_socket)
            elif self.eth_data_array[0] == self.GET_CHANNEL_STATUS:
                self.get_channel_status(client_socket)
            elif self.eth_data_array[0] == self.GET_FIRMWARE_VERSION:
                self.get_firmware_version(client_socket)
            else:
                self.eth_error_response(self.ERROR_TELEGRAM_ID_NOK, client_socket)
        else:
            self.eth_error_response(self.ERROR_CHECKSUM_NOK, client_socket)
    
    def check_length(self):
        """Set telegram length based on telegram ID - equivalent to CheckLength()"""
        if self.eth_input_byte == self.SELECT_CHANNEL:
            self.crc_location = 6
        elif self.eth_input_byte == self.GET_CHANNEL_STATUS:
            self.crc_location = 6
        elif self.eth_input_byte == self.GET_FIRMWARE_VERSION:
            self.crc_location = 5
        
        return self.crc_location
    
    def check_sum(self):
        """Calculate CRC32 checksum - equivalent to CheckSum()"""
        data_for_crc = bytes(self.eth_data_array[:self.crc_location - 4])
        self.checksum = crc32(data_for_crc) & 0xFFFFFFFF
    
    def init_array(self):
        """Reset data array - equivalent to InitArray()"""
        self.eth_data_array = [0] * 10
    
    def eth_error_response(self, error_message, client_socket):
        """Send error response - equivalent to EthErrorResponse()"""
        response = [0xFF, error_message]
        
        # Calculate CRC32 for error response
        data_for_crc = bytes(response)
        checksum = crc32(data_for_crc) & 0xFFFFFFFF
        
        # Add CRC bytes
        response.extend([
            (checksum >> 24) & 0xFF,
            (checksum >> 16) & 0xFF,
            (checksum >> 8) & 0xFF,
            checksum & 0xFF
        ])
        
        # Send error message
        client_socket.send(bytes(response))
        
        # Turn color yellow (red + green)
        self.led.digital_write(self.led.GREEN_LED_PIN, True)
        self.led.digital_write(self.led.RED_LED_PIN, True)
    
    def select_channel_telegram(self, client_socket):
        """Handle select channel telegram - equivalent to SelectChannelTelegram()"""
        # Check if master or slave nibble is correct (exact Arduino logic)
        if ((self.eth_data_array[1] >> 4) == 1) or ((self.eth_data_array[1] >> 4) == 0):
            # Check if port is in range (exact Arduino logic)
            if (self.eth_data_array[1] & 0x0F) <= 8:
                # if telegram is for the master (exact Arduino logic)
                if (self.eth_data_array[1] >> 4) == 0:
                    PortExtenderSetPin(self.eth_data_array[1] & 0x0F, MASTER)
                else:  # if telegram is for the slave
                    PortExtenderSetPin(self.eth_data_array[1] & 0x0F, SLAVE)
                
                # Send response - same as received telegram (Arduino comment: don't need to recalculate CRC32)
                response = self.eth_data_array[:6]
                client_socket.send(bytes(response))
                
                # Turn switch color green (exact Arduino logic)
                self.led.digital_write(self.led.RED_LED_PIN, False)
                self.led.digital_write(self.led.GREEN_LED_PIN, True)
            else:
                self.eth_error_response(self.ERROR_PAYLOAD_NOK, client_socket)
        else:
            self.eth_error_response(self.ERROR_PAYLOAD_NOK, client_socket)
    
    def get_channel_status(self, client_socket):
        """Get current channel status - equivalent to GetChannelStatus()"""
        # Check if payload (master/slave) is correct (exact Arduino logic and comment)
        if (self.eth_data_array[1] == 1) or (self.eth_data_array[1] == 0):
            # if telegram is for the master (exact Arduino logic)
            if (self.eth_data_array[1] >> 4) == 0:
                self.eth_data_array[1] = PortExtenderMaster.readOuputStatus(PCAL6408_OUTPUT_REG)
            else:  # if telegram is for the slave
                self.eth_data_array[1] = PortExtenderSlave.readOuputStatus(PCAL6408_OUTPUT_REG)
            
            # Send response (exact Arduino logic)
            client_socket.send(bytes([self.eth_data_array[0]]))  # Telegram ID
            client_socket.send(bytes([self.eth_data_array[1]]))  # Payload - Port Status
            
            # CRC32 has to be calculated every time because of the variable value of the port (Arduino comment)
            data_for_crc = bytes([self.eth_data_array[0], self.eth_data_array[1]])
            checksum = crc32(data_for_crc) & 0xFFFFFFFF
            
            self.eth_data_array[2] = (checksum >> 24) & 0xFF
            self.eth_data_array[3] = (checksum >> 16) & 0xFF
            self.eth_data_array[4] = (checksum >> 8) & 0xFF
            self.eth_data_array[5] = checksum & 0xFF
            
            client_socket.send(bytes([self.eth_data_array[2]]))  # CRC byte 1
            client_socket.send(bytes([self.eth_data_array[3]]))  # CRC byte 2
            client_socket.send(bytes([self.eth_data_array[4]]))  # CRC byte 3
            client_socket.send(bytes([self.eth_data_array[5]]))  # CRC byte 4
            
            # Turn switch color green (exact Arduino logic)
            self.led.digital_write(self.led.RED_LED_PIN, False)
            self.led.digital_write(self.led.GREEN_LED_PIN, True)
        else:
            self.eth_error_response(self.ERROR_PAYLOAD_NOK, client_socket)
    
    def get_firmware_version(self, client_socket):
        """Get firmware version - equivalent to GetFirmwareVersion()"""
        response = [
            self.eth_data_array[0],
            self.FW_VERSION_MAJOR,
            self.FW_VERSION_MINOR
        ]
        
        # Calculate CRC32
        data_for_crc = bytes(response)
        checksum = crc32(data_for_crc) & 0xFFFFFFFF
        
        # Add CRC bytes
        response.extend([
            (checksum >> 24) & 0xFF,
            (checksum >> 16) & 0xFF,
            (checksum >> 8) & 0xFF,
            checksum & 0xFF
        ])
        
        client_socket.send(bytes(response))
        
        # Turn switch color green
        self.led.digital_write(self.led.RED_LED_PIN, False)
        self.led.digital_write(self.led.GREEN_LED_PIN, True)
    
    def eth_receive_telegram(self):
        """Main receive function - equivalent to EthReceiveTelegram()"""
        # In this Python implementation, the actual receiving is handled
        # by the server thread, so this function just maintains the interface
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()