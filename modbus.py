
#!/usr/bin/env python
# Log data from serial port
# https://stackoverflow.com/questions/55111572/convert-rs232-ascii-to-modbus-tcp-using-pymodbus
# Works with pymodbus 2.1.0

#General Libraries and Sensor Lbraries
import time
import board
import adafruit_mprls
import smbus2
import bme280
import Adafruit_ADS1x15
import adafruit_mcp4725
import busio
import random

#setup BME paramets
#compensation_params = bme280.load_calibration_params(smbus2.SMBus(1), 0x76)

#settings
i2c = board.I2C()
mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)
bme = bme280.sample(smbus2.SMBus(1), 0x76)
adc = Adafruit_ADS1x15.ADS1115()
dac = adafruit_mcp4725.MCP4725(busio.I2C(board.SCL, board.SDA))

#ADC Setting
GAIN = 2/3 #Max +/-6.144V

#Global First run Flag
global flag
flag = 1

"""

Pymodbus Server With Updating Thread
--------------------------------------------------------------------------
This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::
    from threading import Thread
    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, Endian

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

builder = BinaryPayloadBuilder(wordorder=Endian.Big, byteorder=Endian.Big)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
def run_once(context):
 """
	This is a Run Once only script to check previous settings from Config file.
        Using the global variable flag to determine if this is a first run or not.
 """
 global flag
 if flag == 1:
  builder.reset()
  print("ran config input")
  config = open("Config.txt","r")
  V = config.read()
  values = V.splitlines()
  print(values)
  values.pop(0)
  Val = []
  for item in values:
   Val.append(float(item))
#   dac.set_value = int(Val[2])
  print(Val)
  for item in Val:
   builder.add_32bit_float(item)
  setreg = builder.to_registers()
  log.debug("settings: " + str(setreg))
  context[0x00].setValues(3, 0x14, setreg)
  builder.reset()
  flag = 0
  return()
 else:
  return()

def sensor_reader():
 """
   This section will read in data from the vaious sensors and return all values as data to be converted into 
   Modbus channels.
  Note: 1hPa = 0.75006mmHg
 """
 compensation_params = bme280.load_calibration_params(smbus2.SMBus(1), 0x76)
 ABSpressure = round(mpr.pressure,4)
 AMBPressure = round(bme.pressure,4)
 GaugePress = round((mpr.pressure - bme.pressure)/2.4908890833333,2)
 temp = round(bme.temperature,2)
 FV = (round(adc.read_adc(2, gain=GAIN),4))
 DV = (round(adc.read_adc(3, gain=GAIN),4))
 data = [ABSpressure, AMBPressure, GaugePress, temp, FV, DV, 1.0]
 print(str(data))
 return(data)

def updating_writer(context):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.
    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    data = sensor_reader()
    context = context
    run_once(context)
    #print(data)
    if data:
        # We can not directly write float values to registers, Use BinaryPayloadBuilder to convert float to IEEE-754 hex integer
        # Reset buffer so that we are not appending to the existing payload from previous iterations.
        builder.reset()
        for d in data:
            builder.add_32bit_float(d)
        registers = builder.to_registers()
        context = context
        register = 3  # Modbus function code (3) read holding registers. Just to uniquely identify what we are reading from /writing in to.
        slave_id = 0x00 # Device Unit address , refer ModbusSlaveContext below
        address = 0x00 # starting offset of register to write (0 --> 40001)
        log.debug("new values: " + str(registers))
        context[slave_id].setValues(register, address, registers)
        

def run_updating_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [100] * 100),
        co=ModbusSequentialDataBlock(0, [100] * 100),
        hr=ModbusSequentialDataBlock(0, [100] * 100),
        ir=ModbusSequentialDataBlock(0, [100] * 100))
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    time = 5  # 5 seconds delay
    loop = LoopingCall(f=updating_writer,
                       context=context)
    loop.start(time, now=False)  # initially delay by time
    StartTcpServer(context, identity=identity, address=("172.16.20.39", 502))

if __name__ == "__main__":
    run_updating_server()

"""
Modbus map:
 Coils:
  0:DAC Status   (If False DAC = 0, If True DAC = reg(40095))
  1:Pump Status  (If False Pump OFF, If True Pump ON)
 Holding Registers: 32bit Channels Sensor Channels
  0-1: Manifold Pressure (MPRLS)
  2-3: Ambient Pressure  (BME280)
  4-5: GaugePressure     (MPRLS-BME280)
  6-7: Tempurature       (BME280)
  8-9: Flow Feedback     (ADS1115 Channel 2)
  10-11: Flow Setting      (ADS1115 Channel 3)
 Hold Registers: 32bit Settings that are User Set and stored in a Config.txt
  20-21: MFC SN     (Taken from MFC)
  22-23: FSlope     (Feedback Reading)
  24-25: FOffset    (Feedback Reading)
  26-27: RSLope     (SetPoint Reading)
  28-29: ROffset    (SetPoint Reading)
  30-31: DACSetting (DAC Last Setpoint)
"""
