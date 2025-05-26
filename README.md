markdown# CAN MUX - Python Port pentru Raspberry Pi 5

Portarea unui proiect Arduino CAN MUX în Python pentru Raspberry Pi 5, menținând sintaxa și logica originală.

## Descrierea Proiectului

CAN MUX este un multiplexor controlat prin Ethernet care gestionează două port extendere I2C (PCAL6408). Permite selectarea canalelor (1-8) pe fiecare port extender prin comenzi primite via TCP/IP.

## Hardware Requirements

- **Raspberry Pi 5**
- **2x PCAL6408** I2C Port Extenders (Master: 0x20, Slave: 0x21)
- **LED RGB** (3 LED-uri separate sau modul RGB)
- **Buton** pentru modul serial
- **Conexiune Ethernet**

## Hardware Connections