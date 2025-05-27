#!/usr/bin/env python3
"""
Script pentru crearea executabilului GUI
Folosește PyInstaller pentru a crea un .exe standalone
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Verifică dacă sunt instalate dependințele necesare"""
    required_modules = ['tkinter', 'socket', 'json', 'threading', 're', 'datetime', 'os']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        return False
    
    # Check paramiko for SSH
    try:
        import paramiko
        print(f"✅ Paramiko found: {paramiko.__version__}")
    except ImportError:
        print("❌ Paramiko not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
            print("✅ Paramiko installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Paramiko")
            return False
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False
    
    return True

def create_icon():
    """Creează un icon simplu pentru aplicație"""
    icon_content = '''
# Simple icon creation (placeholder)
# You can replace this with a proper .ico file
'''
    return None  # Will use default icon

def build_executable():
    """Construiește executabilul cu PyInstaller"""
    
    print("🔨 Building CAN MUX GUI Configurator...")
    
    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single executable file
        "--windowed",          # No console window (for GUI)
        "--name", "CanMuxConfigurator",
        "--distpath", "dist",  # Output directory
        "--workpath", "build", # Work directory
        "--specpath", ".",     # Spec file location
        "can_mux_gui.py"       # Source file
    ]
    
    # Add icon if available
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        pyinstaller_cmd.extend(["--icon", icon_path])
    
    # Add additional options for better compatibility
    pyinstaller_cmd.extend([
        "--clean",                    # Clean PyInstaller cache
        "--noconfirm",               # Replace output directory without confirmation
        "--add-data", "README.md;.",  # Include README if exists
    ])
    
    try:
        print("📦 Running PyInstaller...")
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if executable was created
            exe_path = Path("dist") / "CanMuxConfigurator.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📁 Executable created: {exe_path}")
                print(f"📏 Size: {size_mb:.1f} MB")
                return True
            else:
                print("❌ Executable not found in expected location")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_installer_script():
    """Creează un script de instalare simplu"""
    installer_content = '''@echo off
echo Installing CAN MUX GUI Configurator...
echo.

REM Create program directory
if not exist "C:\\Program Files\\CanMuxConfigurator" mkdir "C:\\Program Files\\CanMuxConfigurator"

REM Copy executable
copy "CanMuxConfigurator.exe" "C:\\Program Files\\CanMuxConfigurator\\"

REM Create desktop shortcut (optional)
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\CAN MUX Configurator.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\CanMuxConfigurator\\CanMuxConfigurator.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo You can now run the application from:
echo - Desktop shortcut: CAN MUX Configurator
echo - Direct path: C:\\Program Files\\CanMuxConfigurator\\CanMuxConfigurator.exe
echo.
pause
'''
    
    with open("dist/install.bat", "w") as f:
        f.write(installer_content)
    
    print("📦 Installer script created: dist/install.bat")

def create_readme():
    """Creează un README pentru distributie"""
    readme_content = '''# CAN MUX GUI Configurator

## Descriere
Aplicație GUI pentru configurarea remotă a dispozitivului CAN MUX care rulează pe Raspberry Pi.

## Instalare
1. Rulează `install.bat` ca Administrator pentru instalare automată
   SAU
2. Copiază `CanMuxConfigurator.exe` într-o locație dorită

## Utilizare
1. Asigură-te că Raspberry Pi cu CAN MUX este pornit și conectat la rețea
2. Pornește aplicația GUI
3. Introdu IP-ul Raspberry Pi (default: 192.168.5.11)
4. Apasă "Connect"
5. Modifică configurațiile dorite
6. Apasă "Update" pentru a salva modificările

## Configurații disponibile
- MAC Address (format: XX.XX.XX.XX.XX.XX)
- IP Address (format: XXX.XXX.XXX.XXX)
- Subnet Mask (format: XXX.XXX.XXX.XXX)
- Gateway (format: XXX.XXX.XXX.XXX)
- DNS (format: XXX.XXX.XXX.XXX)

## Porturi utilizate
- Port 3363: Comunicare principală CAN MUX
- Port 3364: Server de configurare pentru GUI

## Cerințe sistem
- Windows 7/8/10/11
- Conexiune la rețeaua unde se află Raspberry Pi
- Firewall: permisiuni pentru conexiuni outbound pe portul 3364

## Depanare
- Verifică că Raspberry Pi este pornit și conectat la rețea
- Verifică că IP-ul introdus este corect
- Verifică că portul 3364 nu este blocat de firewall
- Verifică log-urile din aplicație pentru detalii despre erori

## Versiune
v1.0 - Configurare remotă CAN MUX
'''
    
    with open("dist/README.txt", "w") as f:
        f.write(readme_content)
    
    print("📝 README created: dist/README.txt")

def main():
    """Funcția principală"""
    print("🚀 CAN MUX GUI Builder")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return False
    
    # Check if source file exists
    if not os.path.exists("gui.py"):
        print("❌ Source file 'gui.py' not found!")
        print("   Make sure you have the GUI source code in the current directory")
        return False
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        return False
    
    # Create additional files
    create_installer_script()
    create_readme()
    
    print("\n" + "=" * 50)
    print("✅ Build completed successfully!")
    print("\n📁 Files created in 'dist' directory:")
    print("   - CanMuxConfigurator.exe (main application)")
    print("   - install.bat (installer script)")
    print("   - README.txt (user manual)")
    print("\n🚀 You can now distribute the 'dist' folder or just the .exe file")
    print("\n💡 To install on target computer:")
    print("   1. Copy dist folder to target computer")
    print("   2. Run install.bat as Administrator")
    print("   3. Use desktop shortcut or run from Program Files")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)