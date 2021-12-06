src = 0x584D417F44434D46
src2 = 0x6A656C417C65615B
src3 = 0x44454E62           # dword
src4 = 0x6840               # word

result_bytes = src.to_bytes(8, 'little') + src2.to_bytes(8, 'little') + src3.to_bytes(4, 'little') + src4.to_bytes(2, 'little')

print("Original Bytes: " + str(result_bytes))

result = ""
for i in range(0x15+1):
    result += chr(i ^ result_bytes[i])

print("After Conversion: " + result)