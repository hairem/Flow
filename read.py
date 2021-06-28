from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('172.16.20.39', 502)
client.write_coil(0, False)
client.write_coil(1, True)
result = client.read_coils(0,2)
print(result.bits)
client.close()
