# 0x03 Reverse

## Homework - Fifo

這題內容其實還滿清楚的，雖然簡單，但是該有的概念都有，Decoded File (T1140), NX Bit, 各種 Linux 的 syscall，解一解有種越解越好完的感覺。

Main Function 一開始有一大堆的寫死的資料，透過某個 Function 去轉換:

![FMfb](resource/fifo_main_first_block.png)

簡單看了一下這邊的結構以及 `0x12E9` 的函式，感覺上來說這是一個 Decode Function，而 Key 存放的位置在 `0x2020`。這時候有幾種選擇，第一是去 Reverse `0x12E9` 的 decode function，第二種是直接把程式 run 起來，透過 GDB 的 Breakpoint 觀察 stack 中的值直接取的 decoded data。我是選用第二種方法，得到的結果如下：

- `rbp-0x70` Path: `/tmp/bnpkevsekfpk3`
- `rbp-0x30` Full Path: `/tmp/bnpkevsekfpk3/aw3movsdirnqw` (FIFO Name)
- `rbp-0x50` File: `/tmp/khodsmeogemgoe` (ELF Writing Point)
- `.data: 0x4040`: A Big Data Chunk, Looks like a ELF File Format (by using `x/s`)

![FGsfb](resource/fifo_gdb_stack_fb.png)

接著 reverse `Main` 剩餘的部分，可以發現程式接下來的邏輯如下:

- 把剛剛那一大塊 ELF 的資料寫入 `/tmp/khodsmeogemgoe` 這個檔案
- Fork 出一個 child 去執行上面那隻 ELF
- 檢查並新增 `/tmp/bnpkevsekfpk3/aw3movsdirnqw` 這個 FIFO 檔 (`mkfifo`)
- open fifo pipe, 並寫入 `0xD8` 長度的 decode_key
- 關掉檔案，結束

看完了 Fifo，下一個 Reverse 的對象就是剛剛寫出的 ELF 檔 `/tmp/khodsmeogemgoe`。這支的行為有以下幾個:

- 讀取 Fifo 中的資料
- 重新用同樣的 Decode function 去 decode 出我們最終的 Flag。

Reverse 到這邊才發現，原來 `0x2020` 後面還藏有一段 instructions，在看到 `mov rax, [rbp+var_108]; call rax;` 後檢查一下這支 Binary NX-bit 是沒開的，所以理論上還需要繼續 Reverse 下一段程式碼 (最後還是有 Reverse 了一下，是一段用到 socket 的程式碼)，但我用 gdb 跑所以就看到 flag 了，算是意外得到 flag 了 XD

![fgsb](resource/gdb_view_of_flag.png)

![fimc](resource/gdb_in_memory_code.png)

## Homework - giveUFlag

TLSCallback

- https://docs.microsoft.com/en-us/cpp/parallel/thread-local-storage-tls?view=msvc-170
- http://lallouslab.net/2017/05/30/using-cc-tls-callbacks-in-visual-studio-with-your-32-or-64bits-programs/

TLS Option Section 有寫

### start - 0x401180

- It has sleep mechanism for 0x3E8 millieseconds
- _initterm
  - There are two _initterm to Two functions: `sub_401130`, `sub_401010`

`sub_401010`

- gui app ? console app ?

### sub_0x401940

- Being call twice, first b4 main, second in main

sleep a lot and give u img and give u flag

`YOU_USE_HAIYA_WHEn_YOU'RE_DISAPPOINTED_MMSSGG`

Flag: `FLAG{PaRs1N6_PE_aNd_D11_1S_50_C00111!!!!!111}`

怎麼感覺真的是在 give u Flag....
