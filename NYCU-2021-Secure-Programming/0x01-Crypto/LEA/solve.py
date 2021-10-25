from pwn import *
from math import sin, ceil

# context.log_level = "debug"

def MyCrack(vector, k):
    # Size = 128 * k + 6 (&&flag)
    s = "&&flag".encode()
    A = vector[0]
    B = vector[3]
    C = vector[2]
    D = vector[4]
    E = vector[5]
    F = vector[1]
    def G(X,Y,Z):
        return (X ^ (~Z | ~Y) ^ Z) & 0xFFFFFFFF
    def H(X,Y):
        return (X << Y | X >> (32 - Y)) & 0xFFFFFFFF
    X = [int((0xFFFFFFFE) * sin(i)) & 0xFFFFFFFF for i in range(256)]
    s_size = 128 * k + len(s)
    s += bytes([0x80])
    if len(s) % 128 > 120:
        while len(s) % 128 != 0: s += bytes(1)
    while len(s) % 128 < 120: s += bytes(1)
    # May pad to 120 bytes or 128 + 120 bytes
    # Add 8 Byte Message Length (in Bits)
    s += bytes.fromhex(hex(s_size * 8)[2:].rjust(16, '0'))
    # Final Str => 128 Bytes * k
    for i, b in enumerate(s):
        # 32 Bytes a Block
        k, l = int(b), i & 0x1f
        A = (B + H(A + G(B,C,D) + X[k], l)) & 0xFFFFFFFF
        B = (C + H(B + G(C,D,E) + X[k], l)) & 0xFFFFFFFF
        C = (D + H(C + G(D,E,F) + X[k], l)) & 0xFFFFFFFF
        D = (E + H(D + G(E,F,A) + X[k], l)) & 0xFFFFFFFF
        E = (F + H(E + G(F,A,B) + X[k], l)) & 0xFFFFFFFF
        F = (A + H(F + G(A,B,C) + X[k], l)) & 0xFFFFFFFF
    return ''.join(map(lambda x : hex(x)[2:].rjust(8, '0'), [A, F, C, B, D, E])).encode()

def generate_initial_padding(mes_size):
    s = b""
    s += bytes([0x80])
    if (len(s)+mes_size) % 128 > 120:
        while (len(s)+mes_size) % 128 != 0: s += bytes(1)
    while (len(s)+mes_size) % 128 < 120: s += bytes(1)
    # May pad to 120 bytes or 128 + 120 bytes
    # Add 8 Byte Message Length (in Bits)
    s += bytes.fromhex(hex(mes_size * 8)[2:].rjust(16, '0'))
    return s

p = remote("edu-ctf.csie.org", 42073)

# User Setting
user = b"Admin"
# password = b"pass"

# First Input
p.recvuntil(b"Please Input your username: ")
p.sendline(user)
# p.recvuntil(b"Let's set a password: ")
# p.sendline(password)

# Extract Session and Mac
p.recvuntil(b"Here is your session ID: ")
session = p.recvline()[:-1]
p.recvuntil(b"and your MAC(username&&password&&sessionID): ")
mac = p.recvline()[:-1]

# Pwn
vector = []
for i in range(6):
    vector.append(int(mac[i*8: (i+1)*8], 16))

# Check Password
for i in range(1, 100):
    p.recvuntil(b"What do you want to do? ")
    msglen = len(user) + len(session) + 4 + i
    old_padding = generate_initial_padding(msglen)
    new_mac = MyCrack(vector, ceil(msglen/128))

    p.sendline(b"&&".join([new_mac, session+old_padding, b"flag"]).hex().encode())

    respond = p.recvline()
    if b'Refused!' in respond:
        continue
    else:
        print(b"flag: " + respond)
        break


p.close()