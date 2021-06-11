# SJVAPCD Booster Pump Flow Controller and Manifold Pressure Monitor
This project is intended to control and Teledyne Hastings 10 liter flow controller. It will use a ADS1115 as an ADC, a MPRLS for manifold pressure, a BME280 for ambient pressure and a MCP4725 to control the voltage output. I am planning on building this to run  on a Raspberry Pi Zero for its size. There will be Modbus componenets and a web interface componet based on a website hosted on the system.

#Setup.txt 

This document is where I will be storing the libraries and manager used import said libraries so I can recover is needed.

#Notes:

1. I will need to make a config file to store long term values as well as recover last settings so when system is rebooted it will return to its previous state.
2. This will need to be a compiled program so it can be installed without installing the additional libraries and to lock library versions long term.
3. 
