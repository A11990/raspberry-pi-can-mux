#!/usr/bin/env python3
"""
CAN MUX Programmer & Configurator
GUI similar cu Arduino IDE pentru programarea și configurarea Raspberry Pi
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import socket
import json
import threading
import re
import os
import paramiko
import time
import subprocess
from datetime import datetime

class CanMuxProgrammer:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN MUX Programmer & Configurator v1.0")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # Variabile pentru conexiune
        self.raspberry_ip = tk.StringVar(value="192.168.1.10")
        self.ssh_username = tk.StringVar(value="pi")
        self.ssh_password = tk.StringVar()
        self.project_path = tk.StringVar()
        self.connection_status = tk.StringVar(value="Disconnected")
        self.program_status = tk.StringVar(value="Unknown")
        
        # SSH connection
        self.ssh_client = None
        
        # Variabile pentru configurație
        self.config_vars = {
            'mac': tk.StringVar(value="60.6D.3C.F1.7E.A0"),
            'ip': tk.StringVar(value="192.168.1.10"),
            'subnet_mask': tk.StringVar(value="255.255.255.0"),
            'gateway': tk.StringVar(value="192.168.1.1"),
            'dns': tk.StringVar(value="192.168.1.1")
        }
        
        self.create_widgets()
        self.center_window()
        
    def center_window(self):
        """Centrează fereastra pe ecran"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Creează interfața grafică"""
        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Program Upload
        self.upload_frame = ttk.Frame(notebook)
        notebook.add(self.upload_frame, text="📤 Program Upload")
        self.create_upload_tab()
        
        # Tab 2: Network Configuration
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="🔧 Network Config")
        self.create_config_tab()
        
        # Tab 3: Monitor & Control
        self.monitor_frame = ttk.Frame(notebook)
        notebook.add(self.monitor_frame, text="📊 Monitor")
        self.create_monitor_tab()
        
        # Status bar
        self.create_status_bar()
        
    def create_upload_tab(self):
        """Tab pentru upload program"""
        # Connection section
        conn_frame = ttk.LabelFrame(self.upload_frame, text="Raspberry Pi Connection", padding="10")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Connection controls
        controls_frame = ttk.Frame(conn_frame)
        controls_frame.pack(fill=tk.X)
        
        ttk.Label(controls_frame, text="IP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=self.raspberry_ip, width=15).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(controls_frame, text="User:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=self.ssh_username, width=10).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(controls_frame, text="Password:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=self.ssh_password, show="*", width=12).grid(row=0, column=5, padx=(0, 10))
        
        self.connect_btn = ttk.Button(controls_frame, text="Connect", command=self.connect_raspberry)
        self.connect_btn.grid(row=0, column=6, padx=(10, 0))
        
        # Status
        status_frame = ttk.Frame(conn_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, text="Connection:").pack(side=tk.LEFT)
        self.conn_status_label = ttk.Label(status_frame, textvariable=self.connection_status, foreground="red")
        self.conn_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(status_frame, text="Program:").pack(side=tk.LEFT, padx=(20, 0))
        self.prog_status_label = ttk.Label(status_frame, textvariable=self.program_status, foreground="orange")
        self.prog_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Project section
        project_frame = ttk.LabelFrame(self.upload_frame, text="CAN MUX Project", padding="10")
        project_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Project path
        path_frame = ttk.Frame(project_frame)
        path_frame.pack(fill=tk.X)
        
        ttk.Label(path_frame, text="Project Folder:").pack(side=tk.LEFT)
        ttk.Entry(path_frame, textvariable=self.project_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        ttk.Button(path_frame, text="Browse...", command=self.browse_project).pack(side=tk.RIGHT)
        
        # Project info
        self.project_info = tk.Text(project_frame, height=6, state=tk.DISABLED)
        self.project_info.pack(fill=tk.X, pady=(10, 0))
        
        # Upload controls
        upload_frame = ttk.LabelFrame(self.upload_frame, text="Program Upload", padding="10")
        upload_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(upload_frame)
        button_frame.pack()
        
        self.verify_btn = ttk.Button(button_frame, text="🔍 Verify Project", command=self.verify_project, state=tk.DISABLED)
        self.verify_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.upload_btn = ttk.Button(button_frame, text="📤 Upload & Install", command=self.upload_program, state=tk.DISABLED)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="▶️ Start Program", command=self.start_program, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Program", command=self.stop_program, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Progress
        self.upload_progress = ttk.Progressbar(upload_frame, mode='determinate')
        self.upload_progress.pack(fill=tk.X, pady=(10, 0))
        
    def create_config_tab(self):
        """Tab pentru configurarea rețelei"""
        # Current configuration
        current_frame = ttk.LabelFrame(self.config_frame, text="Current Configuration", padding="10")
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.current_config_text = tk.Text(current_frame, height=8, state=tk.DISABLED)
        self.current_config_text.pack(fill=tk.X)
        
        refresh_frame = ttk.Frame(current_frame)
        refresh_frame.pack(pady=(10, 0))
        
        self.refresh_btn = ttk.Button(refresh_frame, text="🔄 Refresh Configuration", 
                                     command=self.refresh_config, state=tk.DISABLED)
        self.refresh_btn.pack()
        
        # New configuration
        new_frame = ttk.LabelFrame(self.config_frame, text="Network Configuration", padding="10")
        new_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuration inputs
        config_grid = ttk.Frame(new_frame)
        config_grid.pack(fill=tk.X)
        
        configs = [
            ("MAC Address (XX.XX.XX.XX.XX.XX):", "mac"),
            ("IP Address:", "ip"), 
            ("Subnet Mask:", "subnet_mask"),
            ("Gateway:", "gateway"),
            ("DNS Server:", "dns")
        ]
        
        self.config_entries = {}
        for i, (label, key) in enumerate(configs):
            ttk.Label(config_grid, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            entry = ttk.Entry(config_grid, textvariable=self.config_vars[key], width=25)
            entry.grid(row=i, column=1, sticky=tk.W, pady=5, padx=(0, 20))
            self.config_entries[key] = entry
            
            # Individual save button
            btn = ttk.Button(config_grid, text=f"💾 Save {key.replace('_', ' ').title()}", 
                           command=lambda k=key: self.save_single_config(k), state=tk.DISABLED)
            btn.grid(row=i, column=2, pady=5)
            self.config_entries[f"{key}_btn"] = btn
        
        # Save all button
        save_frame = ttk.Frame(new_frame)
        save_frame.pack(pady=(20, 0))
        
        self.save_all_btn = ttk.Button(save_frame, text="💾 Save All Configuration", 
                                      command=self.save_all_config, state=tk.DISABLED)
        self.save_all_btn.pack()
        
        # Apply & Restart
        restart_frame = ttk.Frame(new_frame)
        restart_frame.pack(pady=(10, 0))
        
        self.apply_restart_btn = ttk.Button(restart_frame, text="🔄 Apply & Restart Program", 
                                           command=self.apply_and_restart, state=tk.DISABLED)
        self.apply_restart_btn.pack()
        
    def create_monitor_tab(self):
        """Tab pentru monitorizare"""
        # System info
        info_frame = ttk.LabelFrame(self.monitor_frame, text="System Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_info = tk.Text(info_frame, height=8, state=tk.DISABLED)
        self.system_info.pack(fill=tk.X)
        
        # Controls
        control_frame = ttk.Frame(info_frame)
        control_frame.pack(pady=(10, 0))
        
        self.refresh_info_btn = ttk.Button(control_frame, text="🔄 Refresh Info", 
                                          command=self.refresh_system_info, state=tk.DISABLED)
        self.refresh_info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reboot_btn = ttk.Button(control_frame, text="🔄 Reboot Raspberry Pi", 
                                    command=self.reboot_raspberry, state=tk.DISABLED)
        self.reboot_btn.pack(side=tk.LEFT)
        
        # Real-time log
        log_frame = ttk.LabelFrame(self.monitor_frame, text="Program Output (Real-time)", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.program_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.program_log.pack(fill=tk.BOTH, expand=True)
        
        # Log controls
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(pady=(10, 0))
        
        self.start_log_btn = ttk.Button(log_control_frame, text="▶️ Start Live Log", 
                                       command=self.start_live_log, state=tk.DISABLED)
        self.start_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_log_btn = ttk.Button(log_control_frame, text="⏹️ Stop Live Log", 
                                      command=self.stop_live_log, state=tk.DISABLED)
        self.stop_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_log_btn = ttk.Button(log_control_frame, text="🗑️ Clear Log", 
                                       command=self.clear_program_log, state=tk.DISABLED)
        self.clear_log_btn.pack(side=tk.LEFT)
        
    def create_status_bar(self):
        """Creează bara de status"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="Ready - Select project and connect to Raspberry Pi", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
    def set_status(self, message, color="black"):
        """Setează mesajul din bara de status"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
        
    def browse_project(self):
        """Browse pentru folderul proiectului"""
        folder = filedialog.askdirectory(title="Select CAN MUX Project Folder")
        if folder:
            self.project_path.set(folder)
            self.verify_project()
            
    def verify_project(self):
        """Verifică proiectul selectat"""
        if not self.project_path.get():
            return
            
        folder = self.project_path.get()
        if not os.path.exists(folder):
            self.set_status("Project folder not found!", "red")
            return
            
        # Fișierele necesare pentru CAN MUX
        required_files = [
            "main.py", "config_server.py", "config_manager.py", 
            "ethernet_receive.py", "led_control.py", "requirements.txt"
        ]
        
        found_files = []
        missing_files = []
        
        for file in required_files:
            file_path = os.path.join(folder, file)
            if os.path.exists(file_path):
                found_files.append(file)
            else:
                missing_files.append(file)
        
        # Optional files
        optional_files = ["serial_menu.py", "port_extender.py", "gpio_pi5.py"]
        for file in optional_files:
            file_path = os.path.join(folder, file)
            if os.path.exists(file_path):
                found_files.append(file)
        
        # Update project info
        self.project_info.config(state=tk.NORMAL)
        self.project_info.delete(1.0, tk.END)
        
        info_text = f"📁 Project: {os.path.basename(folder)}\n"
        info_text += f"📍 Path: {folder}\n\n"
        info_text += f"✅ Found files ({len(found_files)}):\n"
        for file in found_files:
            info_text += f"   • {file}\n"
        
        if missing_files:
            info_text += f"\n❌ Missing files ({len(missing_files)}):\n"
            for file in missing_files:
                info_text += f"   • {file}\n"
        
        # Check file sizes
        total_size = 0
        for file in found_files:
            file_path = os.path.join(folder, file)
            size = os.path.getsize(file_path)
            total_size += size
        
        info_text += f"\n📊 Total size: {total_size/1024:.1f} KB"
        
        if missing_files:
            info_text += "\n\n⚠️  Some required files are missing!"
            status_msg = f"Project verification: {len(missing_files)} missing files"
            status_color = "orange"
        else:
            info_text += "\n\n✅ Project is ready for upload!"
            status_msg = "Project verified successfully"
            status_color = "green"
        
        self.project_info.insert(1.0, info_text)
        self.project_info.config(state=tk.DISABLED)
        
        self.set_status(status_msg, status_color)
        
    def connect_raspberry(self):
        """Conectare la Raspberry Pi"""
        if self.ssh_client:
            self.disconnect_raspberry()
            return
            
        if not self.ssh_password.get():
            messagebox.showerror("Error", "Please enter SSH password")
            return
            
        # Start connection în thread
        threading.Thread(target=self._connect_thread, daemon=True).start()
        
    def _connect_thread(self):
        """Thread pentru conectarea SSH"""
        try:
            self.set_status("Connecting to Raspberry Pi...", "orange")
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.raspberry_ip.get(),
                username=self.ssh_username.get(),
                password=self.ssh_password.get(),
                timeout=10
            )
            
            # Update UI în main thread
            self.root.after(0, self._connection_success)
            
        except Exception as e:
            self.root.after(0, lambda: self._connection_failed(str(e)))
            
    def _connection_success(self):
        """Callback pentru conexiune reușită"""
        self.connection_status.set("Connected")
        self.conn_status_label.config(foreground="green")
        self.connect_btn.config(text="Disconnect")
        
        # Enable buttons
        buttons_to_enable = [
            self.verify_btn, self.upload_btn, self.start_btn, self.stop_btn,
            self.refresh_btn, self.save_all_btn, self.apply_restart_btn,
            self.refresh_info_btn, self.reboot_btn, self.start_log_btn,
            self.stop_log_btn, self.clear_log_btn
        ]
        
        for btn in buttons_to_enable:
            btn.config(state=tk.NORMAL)
            
        # Enable config buttons
        for key in self.config_vars.keys():
            self.config_entries[f"{key}_btn"].config(state=tk.NORMAL)
        
        self.set_status("Connected to Raspberry Pi", "green")
        
        # Check program status
        self.check_program_status()
        self.refresh_config()
        
    def _connection_failed(self, error):
        """Callback pentru conexiune eșuată"""
        self.connection_status.set("Failed")
        self.conn_status_label.config(foreground="red")
        self.set_status(f"Connection failed: {error}", "red")
        messagebox.showerror("Connection Error", f"Failed to connect:\n{error}")
        
    def disconnect_raspberry(self):
        """Deconectare de la Raspberry Pi"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            
        self.connection_status.set("Disconnected")
        self.conn_status_label.config(foreground="red")
        self.connect_btn.config(text="Connect")
        
        # Disable buttons
        buttons_to_disable = [
            self.verify_btn, self.upload_btn, self.start_btn, self.stop_btn,
            self.refresh_btn, self.save_all_btn, self.apply_restart_btn,
            self.refresh_info_btn, self.reboot_btn, self.start_log_btn,
            self.stop_log_btn, self.clear_log_btn
        ]
        
        for btn in buttons_to_disable:
            btn.config(state=tk.DISABLED)
            
        # Disable config buttons
        for key in self.config_vars.keys():
            self.config_entries[f"{key}_btn"].config(state=tk.DISABLED)
        
        self.set_status("Disconnected from Raspberry Pi", "gray")
        
    def upload_program(self):
        """Upload programul pe Raspberry Pi"""
        if not self.project_path.get():
            messagebox.showerror("Error", "Please select project folder first")
            return
            
        if not self.ssh_client:
            messagebox.showerror("Error", "Please connect to Raspberry Pi first")
            return
            
        # Confirm upload
        if not messagebox.askyesno("Confirm Upload", 
                                  "This will upload and install the CAN MUX program.\n" +
                                  "Any existing program will be replaced.\n\n" +
                                  "Continue?"):
            return
            
        # Start upload în thread
        threading.Thread(target=self._upload_thread, daemon=True).start()
        
    def _upload_thread(self):
        """Thread pentru upload program"""
        try:
            self.root.after(0, lambda: self.set_status("Uploading program...", "orange"))
            self.root.after(0, lambda: self.upload_progress.config(value=0))
            
            # Create project directory
            remote_path = "/home/pi/can_mux"
            self.ssh_client.exec_command(f"mkdir -p {remote_path}")
            self.root.after(0, lambda: self.upload_progress.config(value=10))
            
            # Upload files
            sftp = self.ssh_client.open_sftp()
            
            files_to_upload = []
            for file in os.listdir(self.project_path.get()):
                if file.endswith(('.py', '.txt', '.json', '.md')):
                    files_to_upload.append(file)
            
            total_files = len(files_to_upload)
            uploaded = 0
            
            for file in files_to_upload:
                local_file = os.path.join(self.project_path.get(), file)
                remote_file = f"{remote_path}/{file}"
                
                sftp.put(local_file, remote_file)
                uploaded += 1
                progress = 10 + (uploaded / total_files) * 60
                self.root.after(0, lambda p=progress: self.upload_progress.config(value=p))
                
            sftp.close()
            self.root.after(0, lambda: self.upload_progress.config(value=70))
            
            # Install dependencies
            self.root.after(0, lambda: self.set_status("Installing dependencies...", "orange"))
            stdin, stdout, stderr = self.ssh_client.exec_command(f"cd {remote_path} && pip3 install --user -r requirements.txt")
            stdout.read()  # Wait for completion
            self.root.after(0, lambda: self.upload_progress.config(value=85))
            
            # Create systemd service
            service_content = f"""[Unit]
Description=CAN MUX Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
WorkingDirectory={remote_path}
ExecStart=/usr/bin/python3 {remote_path}/main.py
Restart=always
RestartSec=5
Environment=PYTHONPATH={remote_path}

[Install]
WantedBy=multi-user.target
"""
            
            # Write service file
            stdin, stdout, stderr = self.ssh_client.exec_command(f"echo '{service_content}' | sudo tee /etc/systemd/system/canmux.service")
            stdout.read()
            
            # Enable service
            self.ssh_client.exec_command("sudo systemctl daemon-reload")
            self.ssh_client.exec_command("sudo systemctl enable canmux.service")
            self.root.after(0, lambda: self.upload_progress.config(value=100))
            
            # Success
            self.root.after(0, self._upload_success)
            
        except Exception as e:
            self.root.after(0, lambda: self._upload_failed(str(e)))
            
    def _upload_success(self):
        """Callback pentru upload reușit"""
        self.set_status("Program uploaded successfully!", "green")
        self.upload_progress.config(value=0)
        messagebox.showinfo("Success", 
                           "Program uploaded and installed successfully!\n\n" +
                           "The program is now ready to start.")
        self.check_program_status()
        
    def _upload_failed(self, error):
        """Callback pentru upload eșuat"""
        self.set_status(f"Upload failed: {error}", "red")
        self.upload_progress.config(value=0)
        messagebox.showerror("Upload Error", f"Failed to upload program:\n{error}")
        
    def start_program(self):
        """Pornește programul pe Raspberry Pi"""
        if not self.ssh_client:
            return
            
        try:
            self.set_status("Starting program...", "orange")
            self.ssh_client.exec_command("sudo systemctl start canmux.service")
            time.sleep(2)  # Wait a bit
            self.check_program_status()
            
        except Exception as e:
            self.set_status(f"Failed to start program: {e}", "red")
            
    def stop_program(self):
        """Oprește programul pe Raspberry Pi"""
        if not self.ssh_client:
            return
            
        try:
            self.set_status("Stopping program...", "orange")
            self.ssh_client.exec_command("sudo systemctl stop canmux.service")
            time.sleep(2)  # Wait a bit
            self.check_program_status()
            
        except Exception as e:
            self.set_status(f"Failed to stop program: {e}", "red")
            
    def check_program_status(self):
        """Verifică statusul programului"""
        if not self.ssh_client:
            return
            
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("sudo systemctl is-active canmux.service")
            status = stdout.read().decode().strip()
            
            if status == "active":
                self.program_status.set("Running")
                self.prog_status_label.config(foreground="green")
                self.set_status("Program is running", "green")
            elif status == "inactive":
                self.program_status.set("Stopped")
                self.prog_status_label.config(foreground="red")
                self.set_status("Program is stopped", "red")
            else:
                self.program_status.set(f"Status: {status}")
                self.prog_status_label.config(foreground="orange")
                
        except Exception as e:
            self.program_status.set("Unknown")
            self.prog_status_label.config(foreground="gray")
            
    def refresh_config(self):
        """Refresh configurația curentă"""
        if not self.ssh_client:
            return
            
        try:
            # Read config through Python command
            cmd = """python3 -c "
from config_manager import ConfigManager
cm = ConfigManager()
config = cm.load_network_config()
print('MAC:', config['mac'])
print('IP:', config['ip'])
print('Subnet:', config['subnet_mask'])
print('Gateway:', config['gateway'])
print('DNS:', config['dns'])
" """
            
            stdin, stdout, stderr = self.ssh_client.exec_command(f"cd /home/pi/can_mux && {cmd}")
            output = stdout.read().decode()
            
            self.current_config_text.config(state=tk.NORMAL)
            self.current_config_text.delete(1.0, tk.END)
            
            config_text = "📋 Current Network Configuration:\n"
            config_text += "=" * 40 + "\n"
            config_text += output
            config_text += "\n🕒 Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.current_config_text.insert(1.0, config_text)
            self.current_config_text.config(state=tk.DISABLED)
            
            self.set_status("Configuration refreshed", "green")
            
        except Exception as e:
            self.set_status(f"Failed to refresh config: {e}", "red")
            
    def save_single_config(self, config_type):
        """Salvează o singură configurație"""
        value = self.config_vars[config_type].get().strip()
        if not value:
            messagebox.showwarning("Warning", f"Please enter a value for {config_type}")
            return
            
        self._save_config({config_type: value})
        
    def save_all_config(self):
        """Salvează toată configurația"""
        config_data = {}
        for key, var in self.config_vars.items():
            value = var.get().strip()
            if value:
                config_data[key] = value
                
        if not config_data:
            messagebox.showwarning("Warning", "Please enter at least one configuration value")
            return
            
        self._save_config(config_data)
        
    def _save_config(self, config_data):
        """Salvează configurația pe Raspberry Pi"""
        if not self.ssh_client:
            messagebox.showerror("Error", "Not connected to Raspberry Pi")
            return
            
        try:
            self.set_status("Saving configuration...", "orange")
            
            # Create Python script to update config
            update_script = """
import sys
sys.path.append('/home/pi/can_mux')
from config_manager import EEPROM
from config_manager import (
    EEPROM_IP_ADDRESS_OFFSET, EEPROM_MAC_ADDRESS_OFFSET,
    EEPROM_SUBNET_MASK_ADDRESS_OFFSET, EEPROM_DNS_ADDRESS_OFFSET,
    EEPROM_GATEWAY_ADDRESS_OFFSET, IP_MAX_BYTES, MAC_MAX_BYTES,
    SUBNET_MAX_BYTES, GATEWAY_MAX_BYTES, DNS_MAX_BYTES
)

def parse_mac(mac_str):
    mac_str = mac_str.replace(' ', '').upper()
    if '.' in mac_str:
        parts = mac_str.split('.')
    elif ':' in mac_str:
        parts = mac_str.split(':')
    elif '-' in mac_str:
        parts = mac_str.split('-')
    else:
        if len(mac_str) == 12:
            parts = [mac_str[i:i+2] for i in range(0, 12, 2)]
        else:
            raise ValueError("Invalid MAC format")
    
    if len(parts) != 6:
        raise ValueError("MAC must have 6 parts")
    
    return [int(part, 16) for part in parts]

def parse_ip(ip_str):
    parts = ip_str.split('.')
    if len(parts) != 4:
        raise ValueError("IP must have 4 parts")
    
    ip_bytes = []
    for part in parts:
        byte_val = int(part)
        if not 0 <= byte_val <= 255:
            raise ValueError(f"IP octet {part} out of range")
        ip_bytes.append(byte_val)
    return ip_bytes

# Update configuration
config_data = """ + str(config_data) + """

for config_type, value in config_data.items():
    try:
        if config_type == "mac":
            mac_bytes = parse_mac(value)
            for i in range(MAC_MAX_BYTES):
                EEPROM.update(EEPROM_MAC_ADDRESS_OFFSET + i, mac_bytes[i])
        elif config_type == "ip":
            ip_bytes = parse_ip(value)
            for i in range(IP_MAX_BYTES):
                EEPROM.update(EEPROM_IP_ADDRESS_OFFSET + i, ip_bytes[i])
        elif config_type == "subnet_mask":
            subnet_bytes = parse_ip(value)
            for i in range(SUBNET_MAX_BYTES):
                EEPROM.update(EEPROM_SUBNET_MASK_ADDRESS_OFFSET + i, subnet_bytes[i])
        elif config_type == "gateway":
            gateway_bytes = parse_ip(value)
            for i in range(GATEWAY_MAX_BYTES):
                EEPROM.update(EEPROM_GATEWAY_ADDRESS_OFFSET + i, gateway_bytes[i])
        elif config_type == "dns":
            dns_bytes = parse_ip(value)
            for i in range(DNS_MAX_BYTES):
                EEPROM.update(EEPROM_DNS_ADDRESS_OFFSET + i, dns_bytes[i])
        
        print(f"Updated {config_type}: {value}")
    except Exception as e:
        print(f"Error updating {config_type}: {e}")
        
print("Configuration update completed")
"""
            
            # Execute the update script
            cmd = f"cd /home/pi/can_mux && python3 -c '{update_script}'"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                raise Exception(f"Update error: {error}")
                
            self.set_status("Configuration saved successfully", "green")
            messagebox.showinfo("Success", "Configuration saved to Raspberry Pi!\n\n" + output)
            
            # Refresh to show changes
            self.refresh_config()
            
        except Exception as e:
            self.set_status(f"Failed to save config: {e}", "red")
            messagebox.showerror("Save Error", f"Failed to save configuration:\n{str(e)}")
            
    def apply_and_restart(self):
        """Aplică configurația și restart programul"""
        if not messagebox.askyesno("Confirm Restart", 
                                  "This will restart the CAN MUX program with new configuration.\n" +
                                  "Make sure you have saved the configuration first.\n\n" +
                                  "Continue?"):
            return
            
        try:
            self.set_status("Restarting program with new configuration...", "orange")
            self.ssh_client.exec_command("sudo systemctl restart canmux.service")
            time.sleep(3)  # Wait for restart
            self.check_program_status()
            self.refresh_config()
            
        except Exception as e:
            self.set_status(f"Failed to restart: {e}", "red")
            
    def refresh_system_info(self):
        """Refresh informații sistem"""
        if not self.ssh_client:
            return
            
        try:
            self.set_status("Refreshing system information...", "orange")
            
            # Get system info
            commands = {
                "Hostname": "hostname",
                "Uptime": "uptime",
                "Memory": "free -h",
                "Disk Space": "df -h /",
                "CPU Temperature": "vcgencmd measure_temp",
                "Network Interfaces": "ip addr show",
                "CAN MUX Service": "sudo systemctl status canmux.service --no-pager -l",
                "Active Ports": "sudo netstat -tlnp | grep -E ':(3363|3364)'"
            }
            
            info_text = "🖥️  Raspberry Pi System Information\n"
            info_text += "=" * 50 + "\n\n"
            
            for label, cmd in commands.items():
                try:
                    stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
                    output = stdout.read().decode().strip()
                    if output:
                        info_text += f"📊 {label}:\n{output}\n\n"
                except:
                    info_text += f"❌ {label}: Could not retrieve\n\n"
            
            info_text += f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.system_info.config(state=tk.NORMAL)
            self.system_info.delete(1.0, tk.END)
            self.system_info.insert(1.0, info_text)
            self.system_info.config(state=tk.DISABLED)
            
            self.set_status("System information refreshed", "green")
            
        except Exception as e:
            self.set_status(f"Failed to refresh system info: {e}", "red")
            
    def reboot_raspberry(self):
        """Reboot Raspberry Pi"""
        if not messagebox.askyesno("Confirm Reboot", 
                                  "This will reboot the Raspberry Pi.\n" +
                                  "You will need to reconnect after reboot.\n\n" +
                                  "Continue?"):
            return
            
        try:
            self.set_status("Rebooting Raspberry Pi...", "orange")
            self.ssh_client.exec_command("sudo reboot")
            
            # Disconnect since Pi is rebooting
            self.disconnect_raspberry()
            
            messagebox.showinfo("Reboot", "Raspberry Pi is rebooting.\n" +
                               "Wait about 30 seconds, then reconnect.")
            
        except Exception as e:
            self.set_status(f"Reboot failed: {e}", "red")
            
    def start_live_log(self):
        """Start live log monitoring"""
        if hasattr(self, 'log_thread') and self.log_thread.is_alive():
            return
            
        self.log_running = True
        self.log_thread = threading.Thread(target=self._live_log_thread, daemon=True)
        self.log_thread.start()
        
        self.start_log_btn.config(state=tk.DISABLED)
        self.stop_log_btn.config(state=tk.NORMAL)
        self.set_status("Live log started", "green")
        
    def stop_live_log(self):
        """Stop live log monitoring"""
        self.log_running = False
        self.start_log_btn.config(state=tk.NORMAL)
        self.stop_log_btn.config(state=tk.DISABLED)
        self.set_status("Live log stopped", "orange")
        
    def _live_log_thread(self):
        """Thread pentru live log"""
        try:
            # Start following the journal
            stdin, stdout, stderr = self.ssh_client.exec_command("sudo journalctl -u canmux.service -f --no-pager")
            
            while self.log_running:
                line = stdout.readline()
                if line:
                    # Add to log în main thread
                    self.root.after(0, lambda l=line: self._add_log_line(l))
                else:
                    time.sleep(0.1)
                    
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Live log error: {e}", "red"))
            
    def _add_log_line(self, line):
        """Adaugă o linie în log"""
        self.program_log.config(state=tk.NORMAL)
        self.program_log.insert(tk.END, line)
        self.program_log.see(tk.END)
        self.program_log.config(state=tk.DISABLED)
        
    def clear_program_log(self):
        """Șterge log-ul programului"""
        self.program_log.config(state=tk.NORMAL)
        self.program_log.delete(1.0, tk.END)
        self.program_log.config(state=tk.DISABLED)
        
    def on_closing(self):
        """Handler pentru închiderea aplicației"""
        # Stop live log
        if hasattr(self, 'log_running'):
            self.log_running = False
            
        # Disconnect SSH
        if self.ssh_client:
            self.ssh_client.close()
            
        self.root.destroy()

def main():
    """Funcția principală"""
    root = tk.Tk()
    app = CanMuxProgrammer(root)
    
    # Handler pentru închiderea ferestrei
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Pornește aplicația
    root.mainloop()

if __name__ == "__main__":
    main()