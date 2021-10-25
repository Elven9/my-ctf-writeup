from pwn import *

# context.log_level = "debug"

poly = bin(0xaa0d3a677e1be0bf)[2:]

F.<x> = PolynomialRing(GF(2))
P = x^64 + 1
for i in range(1, 64):
    P += int(poly[i]) * x^i
    
C = companion_matrix(P, format='left')

generation = []

for i in range(0, 64):
    # print(f"Generating {42+43*i}th rounds....")
    generation.append((C^(42+43*i))[0])

# Get 64 Result
p = remote("edu-ctf.csie.org", 42069)

result = []
money = 1.2
p.recvuntil(b"> ")
p.send(b"0\n"*64)

for i in range(64):
    # print(f"prv money: {money}")

    nextMoney = float(p.recvline().strip(b" \n>"))

    # print(f"next money: {nextMoney}")

    if nextMoney < money:
        result.append(1)
    else:
        result.append(0)

    money = nextMoney
    # print(result)

# print(result)

b = vector(GF(2), 64, result)
A = matrix(GF(2), 64, generation)
init_state = A^-1*b

sendto = []

for i in range(64, 424):
    tmp = 42+43*i
    res = C^tmp*init_state
    sendto.append(res[0])

# print("\n".join([str(i) for i in sendto]).encode())

p.recvuntil(b"> ")
p.sendline("\n".join([str(i) for i in sendto]).encode())

print(p.recvall().decode())

p.close()
