from pwn import *
from Crypto.Util.number import inverse, long_to_bytes

# context.log_level = "debug"

p = remote("edu-ctf.csie.org", 42071)

# Get n and c
n = int(p.recvline()[4:])
c = int(p.recvline()[4:])
e = 65537

# 128-bit long plaintext
# 128 * 8 * log 2 / log3 roughly equal to 646..... => try 647 times
# Remember to unpad the result
# result: X_0 ~ X_127, remember to reverse when decoding the flag

inverse_3 = inverse(3, n)
result = 0
prior = 0

for i in range(647):
    payload = str((pow(inverse_3, i*e, n) * c) % n).encode()
    p.sendline(payload)

    res = int(p.recvline()[8:])

    next_digit = (res - (prior*inverse_3) % n) % 3

    # Update Prior
    prior = (prior*inverse_3 + next_digit) % n

    # Update Result
    result += pow(3, i) * next_digit

    print(long_to_bytes(result))

p.close()