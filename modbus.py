#!/usr/bin/env python
# Log data from serial port
# https://stackoverflow.com/questions/55111572/convert-rs232-ascii-to-modbus-tcp-using-pymodbus
# Works with pymodbus 2.1.0

import time
import argparse

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
from pymodbus.server.async import StartTcpServer
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

def sensor_reader():
    print("Hello")

def updating_writer(context, device, baudrate):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.
    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    log.debug("device - {}, baudrate-{}".format(device, baudrate))
    data = sensor_reader()
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
        

def run_updating_server(device, baudrate):
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [17] * 100),
        ir=ModbusSequentialDataBlock(0, [17] * 100))
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
                       context=context, device=device, baudrate=baudrate)
    loop.start(time, now=False)  # initially delay by time
    StartTcpServer(context, identity=identity, address=("localhost", 502))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--device", help="device to read from",
                        default="/dev/ttyUSB0")
    parser.add_argument("-s", "--speed", help="speed in bps", default=9600,
                        type=int)
    args = parser.parse_args()
    run_updating_server(args.device, args.speed)
