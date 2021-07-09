from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('172.16.20.45', 502)
client.write_coil(0, True)
client.write_coil(1, False)
result = client.read_coils(0,2)
print(result.bits)
client.close()
