from pwn import *

# context.log_level = "debug"

p = remote("edu-ctf.csie.org", 42070)
ciphertext = bytearray.fromhex(p.recvline()[9:-1].decode("ascii"))

# Process Blocks
originalBlocks = []
for i in range(int(len(ciphertext) / 16)):
    originalBlocks.append(ciphertext[i*16:(i+1)*16])

flags = []
counter = len(originalBlocks)
hasFound = False

# Not decode IV
while counter > 1:
    buf = [bytearray(originalBlocks[counter-2]),bytearray(originalBlocks[counter-1])]

    for i in range(16-1, -1, -1):
        hasFound = False

        for j in range(256):
            if j == originalBlocks[counter-2][i]:
                continue

            p.recvuntil(b"cipher = ")
            buf[0][i] = j
            # print((buf[0]+buf[1]).hex())
            p.sendline((buf[0]+buf[1]).hex())

            recv = p.recvline()
            if b"YESSSSSSSS" in recv:
                hasFound = True
                break
        
        if not hasFound:
            buf[0][i] = originalBlocks[counter-2][i]

        flags.insert(0, chr(buf[0][i] ^ 0x80 ^ originalBlocks[counter-2][i]))
        buf[0][i] ^= 0x80

        print(flags)

    counter -= 1

print("".join(flags))

p.close()