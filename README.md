# SJVAPCD Booster Pump Flow Controller and Manifold Pressure Monitor
This project is intended to control and Teledyne Hastings 10 liter flow controller. It will use a ADS1115 as an ADC, a MPRLS for manifold pressure, a BME280 for ambient pressure and a MCP4725 to control the voltage output. I am planning on building this to run  on a Raspberry Pi Zero for its size. There will be Modbus componenets and a web interface componet based on a website hosted on the system.

#Setup.txt 

This document is where I will be storing the libraries and manager used import said libraries so I can recover is needed.

#Notes:

1. I will need to make a config file to store long term values as well as recover last settings so when system is rebooted it will return to its previous state.
2. This will need to be a compiled program so it can be installed without installing the additional libraries and to lock library versions long term.
3. This will be a 32bit Modbus system with a webpage for interfacing with the unit remotely
4. I am using a 
	Honeywell:
		BME280 : Ambient Pressure, Temperature, and Humidity Sensor
		MPRLS : High Resolution Ported Pressure Sensor 0-25psi Absolute 24bit
	Microchip:
		 MCP4725 : Digital to Analog Convertor 12bit
	Texas Instruments:
		 ADS1115 : Analog to Digital Convertor 16bit
		 TLV2462 : OP-Amp configured as voltage follower
  At the moment I am using pre-made chips from Adafruit but plan to make a custom board using the base parts listed
5. Libraries used will be stored in the Flow_Setup.txt file.
