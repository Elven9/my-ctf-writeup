# HW1 Writeup

## Crypto - nLFSR \[150\]

- Connection: `nc edu-ctf.csie.org 42069`

從題目的名子上來看，這題給的 PRNG 並不能透過簡單的一連串 bit 來預測接下來的輸出，再加上每一次 server 吐出的 number 其實是經過 43 round 的結果 (第一次輸出只經過 42 round)，這讓透過一個一個 bit 去預測的方式更不可行了。

```python
state = int.from_bytes(os.urandom(8), 'little')
poly = 0xaa0d3a677e1be0bf
def step():
    global state
    out = state & 1
    state >>= 1
    if out:
        state ^= poly
    return out
    

def random():
    for _ in range(42):
        step()
    return step()
```

在不斷撞牆的清況下有想過幾個可能：

- `Poly` 的數值會不會讓接下來的輸出有 bias? 經過測試後並不會。
  - 這也是接下來可以吐出固定數量的結果的關鍵，可以幫助我們取得 64 個 equation 重構出 initial state
- Implementation 上有漏洞？有發現每次吐出的 bit 會跟 MSB 的數值一樣，但因為一次的 step 的 iteration 是 43，所以也沒辦法預測出接下來的所有 bit。
  - 雖然這個想法失敗了，但也確認了經過轉換後**下一次的 iteration 的 MSB 跟上一個 iteration 的 LSB 是相同的**這個條件，幫助我們接下來建置 Companion Matrix 可以得到一個 Transform

經果以上一些小實驗後，我們其實可以發現這題雖然是 nLFSR，但在 `GF(2)` 的狀況下 xor 是其實就是加法的概念，我們可以得出一個 Transform Matrix，來 Mapping 每一個 state 的轉換：

```python
poly = bin(0xaa0d3a677e1be0bf)[2:]

F.<x> = PolynomialRing(GF(2))
P = x^64 + 1
for i in range(1, 64):
    P += int(poly[i]) * x^i
    
C = companion_matrix(P, format='left')
```

有了 Transform 後，接下來只要有 64 個解答，就可以還原出 64 bit 的 initial state 了:

```python
# 產生 64 個轉換矩陣
generation = []

for i in range(0, 64):
    # print(f"Generating {42+43*i}th rounds....")
    generation.append((C^(42+43*i))[0])

# 向伺服器取的 64 個結果
# 這邊有個小問題，可能是 pwntools 實作的問題，要一次傳送多筆資料 Server 才不會掛掉
p = remote("edu-ctf.csie.org", 42069)

result = []
money = 1.2
p.recvuntil(b"> ")
p.send(b"0\n"*64)

for i in range(64):
    nextMoney = float(p.recvline().strip(b" \n>"))
    if nextMoney < money:
        result.append(1)
    else:
        result.append(0)
    money = nextMoney
```

取的 64 個結果以及 64 個矩陣後，就可以把這 64 條方程式合在一起計算出一開始的 state 了:

```python
b = vector(GF(2), 64, result)
A = matrix(GF(2), 64, generation)
init_state = A^-1*b
```

取得 State 後就可以預測出接下來伺服器 PRNG 的產出，就可以成功地讓我們的 money 超過 2.5 拉!

```python
sendto = []

for i in range(64, 424):
    tmp = 42+43*i
    res = C^tmp*init_state
    sendto.append(res[0])

p.recvuntil(b"> ")
p.sendline("\n".join([str(i) for i in sendto]).encode())

print(p.recvall().decode())

p.close()
```