#!/usr/bin/env python3
def test_imports():
    modules = ['main', 'gpio_pi5', 'led_control']
    for module in modules:
        try:
            __import__(module)
            print(f"OK: {module}")
        except:
            print(f"ERROR: {module}")
    print("Test complet!")

if __name__ == "__main__":
    test_imports()