# 0x04 Pwn

## Got2Win

Just override read postion with write plt, we can reverse the read process to output to stdout.

## Rop2Win

Use open read write instead of getting shell

## Heapmath

Understand the inner working of the tcache, fastbin

## Market

my previous thought

目標：把 Flag Data 的 Size 設成 0x20 等級的 Chunk，最後 Free 掉他，接著只要用個 size 0x01 的請求，隨便寫個 byte，再印出來就行了。

Actually, Bugs Happened here:

```c++
if (buf[0] == 'n') {
    puts("Sad :(");
    free(admin);
    free(admin->secret);
    admin = NULL;
}
```

It accendentally free the `tcache_perthread_struct`, thus bin `0x20` size had been set to 0, new a user would not get chunk from the cache

Then override the 0x20 tcache subbin head, get the 0x20 chunk, change the starting chunk address

