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

## Single

這題在測試對 ECC 的理解程度。題目給了 output.txt 和產出 output.txt 的程式碼 single.py。從 single.py 中可以看到，這是一個 ECC curve 的 Diffie-Hellman Key Exchange 的過程，而兩個 point A 和 B 會在 output.txt 中可以觀察到：

```python
p = 9631668579539701602760432524602953084395033948174466686285759025897298205383
gx = 5664314881801362353989790109530444623032842167510027140490832957430741393367
gy = 3735011281298930501441332016708219762942193860515094934964869027614672869355
G = Point(gx, gy)
assert is_on_curve(G)

#Alice
dA = random.randint(1, p-2)
A = point_multiply(G, dA)
print('A =', A)

#Bob
dB = random.randint(1, p-2)
B = point_multiply(G, dB)
print('B =', B)
```

所以整理一下我們目前有的資訊:
- p
- G
- A
- B
- Order = p-1

根據 flag 被 encode 的方式，可以確認我們的目標是要找到 A 的 private key，也就是程式碼中的 `dA`：

```python
#Encryption
k = point_multiply(B, dA).x
k = hashlib.sha512(str(k).encode('ascii')).digest()
enc = bytes(ci ^ ki for ci, ki in zip(FLAG.ljust(len(k), b'\0'), k))
print('enc =', enc.hex())
```

Ecc Crypto 的弱點來自於使用的曲線強度如何，所以我們要先求得 a, b 以判別這個曲線是否有特殊性質。求 a, b 的方式也不難，因為我們已經有 `A`, `B` 兩點，即可求得二元方程式：

```python
a = (((A.y^2-A.x^3)-(B.y^2-B.x^3)) / (A.x-B.x)) % p
print(a)
b = (A.y^2-A.x^3-a*A.x)%p
print(b)
```

得到 a 跟 b 後嘗試使用 sage 內建的 EllipticCurve 去產出一個 Curve，但 sage 馬上爆出這是一個 singular curve，sage 並不接受這條 curve。簡報中有提到兩種方法可以處理 singuler curve，但從 order 的 factor 來看這個曲線有 smooth order 的現象：

```python
fs = factor(p-1)
print(fs)
# Output: 2 * 2329468847 * 2414146711 * 2484441769 * 2546315801 * 2988745687 * 3048801089 * 3618313243 * 4105685383
```

所以我們接下來使用 Pohlig-Hellman 來處理這個 curve。但下一個問題是，因為我們不能使用 sage 內建的 elliptic curve，也就是我們不能直接使用內建的 bsgs，必須要自己建一個 bsgs。

```python
# bsgs
def my_bsgs(a, b, n):
    m = ceil(sqrt(n))
    
    table = {}
    
    prevPoint = O
    # Compute Table of J*Gi
    for j in range(0, m):
        table[prevPoint] = j
        prevPoint = point_addition(prevPoint, a)
            
    gama = b
    constant_m_alpha = point_inverse(point_multiply(a, m))

    for i in range(0, m):
        # Search
        if gama in table:
            print("found: " + str(i*m+table[gama]))
            return i*m+table[gama]

        gama = point_addition(gama, constant_m_alpha)
        
    print("Solution Not Found")
    return None
```

整個 Pohlig-Hellman 演算法：

```python
xis = []

for fac in fs:
    gi = point_multiply(G, n//fac[0])
    pi = point_multiply(A, n//fac[0])
    
    di = my_bsgs(gi, pi, fac[0])
    xis.append(di)

da = crt(xis, [fac[0] for fac in fs])
print(da)
```

執行完後最終得到 `dA` 後就可以還原出我們的 key 了：

```python
# Decode
encode_flag = bytes.fromhex(enc)
k = point_multiply(B, da).x
k = hashlib.sha512(str(k).encode('ascii')).digest()
flag = bytes(ci ^^ ki for ci, ki in zip(encode_flag, k))
print('flag =', flag)
```

