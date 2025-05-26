#!/usr/bin/env python3
import time
import threading 
import sys

# Patch pentru a vedea toate mesajele
def debug_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

# Import și patch toate modulele
import ethernet_receive

# Patch funcțiile importante
original_server_loop = ethernet_receive.EthernetReceive._server_loop
original_process_byte = ethernet_receive.EthernetReceive._process_byte

def debug_server_loop(self):
    debug_print("🔗 Server loop started, waiting for connections...")
    while self.running:
        try:
            debug_print("📱 Listening for client...")
            self.client_socket, client_address = self.server_socket.accept()
            debug_print(f"✅ Client connected from {client_address}")
            
            client_thread = threading.Thread(
                target=self._handle_client, 
                args=(self.client_socket,), 
                daemon=True
            )
            client_thread.start()
            
        except Exception as e:
            if self.running:
                debug_print(f"❌ Server error: {e}")
                time.sleep(1)

def debug_process_byte(self, byte_val, client_socket):
    if self.index == 0:
        debug_print(f"📡 New telegram: 0x{byte_val:02X}")
        
    original_process_byte(self, byte_val, client_socket)
    
    if self.index == 0:  # After processing (reset happened)
        debug_print(f"✅ Telegram processed and sent back")

# Apply patches
ethernet_receive.EthernetReceive._server_loop = debug_server_loop
ethernet_receive.EthernetReceive._process_byte = debug_process_byte

# Import restul după patch
from test_mode import TestCanMux

if __name__ == "__main__":
    debug_print("🚀 Starting CAN MUX with DEBUG")
    test_app = TestCanMux()
    test_app.run()