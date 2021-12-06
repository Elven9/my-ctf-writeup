src = [0x3B30142813141A11, 0x3D3538321E022C3A, 0x29302E13, 0x3F33]
length = [8, 8, 4, 2]

encode_bytes = b"".join([src[i].to_bytes(length[i], 'little') for i in range(4)])

result = ""

for i in range(0x15+1):
    tmp = encode_bytes[i] ^ i
    tmp ^= 0x57

    result += chr(tmp)

print("Flag: " + result)

