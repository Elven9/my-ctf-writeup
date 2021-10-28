# 0x01 Crypto Writeup

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

## Crypto - Single \[200\]

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

## Crypto - HNP Revenge \[250\]

這題跟這星期的 lab HNP 的 code 基本上是一模一樣的，唯一的差別是在選 K 的方式。不同於 lab 那題兩次加密之間 K 值是一個線性關係，這次則是把 k 的選擇方式換成**一段固定 hash 值加上另一段由 D 產生的數值加上 message 產出的 hash 值**，得到 k 的選擇：

```python
h = sha256(msg.encode()).digest()
k = int(md5(b'secret').hexdigest() + md5(long_to_bytes(prikey.secret_multiplier) + h).hexdigest(), 16)
sig = prikey.sign(bytes_to_long(h), k)
print(f'({sig.r}, {sig.s})')
```

所以我們接下來的解題方向就是用 Lattice 去解這個已經知道大部分 MSB 的 K (小 k 數值計算)。先整理一下計算公式：

```python
# 因為我們的 MSB 並不是全部為 0、傳統解小 k 的方法，所以我們需要修改一下原本公式中的常數項計算方式
t = (-1* inverse(s1, n)*s2*r1*inverse(r2, n)) %n
u = (inverse(s1, n)*r1*h2*inverse(r2, n) - inverse(s1, n) * h1 + (t+1)*baseK) %n
```

這裡有個雷需要注意一下，我們可以完全確定 128 bit 數是，但是可以觀察到 `Sqrt(n)` 的數值其實比 `2^128` 小，所以我們選擇 K 的時候要選 `2^127`，以及等等需要 Try 幾次直到剛剛好知道 129 個 bit 的那一次才會成功

```python
>>> from ecdsa import SECP256k1
>>> from math import sqrt, ceil
>>> SECP256k1.order
mpz(115792089237316195423570985008687907852837564279074904382605163141518161494337)
>>> ceil(sqrt(SECP256k1.order))
340282366920938425684442744474606501888
>>> 2**128
340282366920938463463374607431768211456
>>>
```

選好 K 後就可以建構我們的 LLL methods 了：

```python
h1 = bytes_to_long(sha256("A".encode()).digest())
r1 = 58084863080992072580334022005567931021154043643259552401385782172570240816523
s1 = 107712904646841307549216306134569074827075078269914988676888071413702894680658

h2 = bytes_to_long(sha256("B".encode()).digest())
r2 = 100750964988822020802724921911452399593227921044610135806466924123392451666453
s2 = 100048223890738129273755755203911968532962608890184062887455576356224860362848

t = (-1* inverse(s1, n)*s2*r1*inverse(r2, n)) %n
u = (inverse(s1, n)*r1*h2*inverse(r2, n) - inverse(s1, n) * h1 + (t+1)*baseK) %n
K = 2^127

B = matrix(ZZ, [[n, 0, 0], [t, 1, 0], [u, 0, K]])
B.LLL()

# 執行結果：
# [ 118896613776238449478129936428974463840  -32806342291851023802586340638786914878  170141183460469231731687303715884105728]
# [-196032320073347428542397021099225337843   96291860774951207159831053703429490718  170141183460469231731687303715884105728]
# [-221830141883562033496969161916984809373 -276742487483606481063492584316071339063                                        0]
```

選出第二列的 base vector 出來得到 K1, K2 後，就可以得到 d 了：

```python
d = ((s1 * (196032320073347428542397021099225337843 + baseK)  - h1) * inverse(r1, n)) %n

# 105228346465649343550315876720427581326892142235257410156707131772573340314147
```

重建出 ecdst 後自行簽章 `Kuruma`，丟回 Server 後就可以得到我們的 Flag 了

```python
from random import randint
from Crypto.Util.number import *
from hashlib import sha256, md5
from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key, Private_key, Signature
from math import sqrt, ceil

E = SECP256k1
G, n = E.generator, E.order

d = 105228346465649343550315876720427581326892142235257410156707131772573340314147
pubkey = Public_key(G, d*G)
prikey = Private_key(pubkey, d)
print(f'P = ({pubkey.point.x()}, {pubkey.point.y()})')

h = sha256("Kuruwa".encode()).digest()
k = int(md5(b'secret').hexdigest() + md5(long_to_bytes(prikey.secret_multiplier) + h).hexdigest(), 16)
sig = prikey.sign(bytes_to_long(h), k)
print(f'({sig.r}, {sig.s})')
```
