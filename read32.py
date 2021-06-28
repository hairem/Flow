from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient

def validator(instance):
    if not instance.isError():
        '''.isError() implemented in pymodbus 1.4.0 and above.'''
        decoder = BinaryPayloadDecoder.fromRegisters(
            instance.registers,
            byteorder=Endian.Big, wordorder=Endian.Little
        )
        return float('{0:.2f}'.format(decoder.decode_32bit_float()))

    else:
        # Error handling.
        print("There isn't the registers, Try again.")
        return None


client = ModbusTcpClient('172.16.20.39', port=502)  # Specify the port.
connection = client.connect()

if connection:
    request = client.read_holding_registers(22, 2, unit=1)  # Specify the unit.
    data = validator(request)
    print(data)

    request = client.read_holding_registers(22, 2, unit=1)  # Specify the unit.
    data = validator(request)
    print(data)

    client.close()

else:
    print('Connection lost, Try again')
