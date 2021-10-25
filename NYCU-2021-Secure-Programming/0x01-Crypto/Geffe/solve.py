# Correlation Attack
import hashlib
from itertools import combinations
from tqdm import tqdm
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random.random import getrandbits

class LFSR:
    def __init__(self, key, taps):
        d = max(taps)
        assert len(key) == d, "Error: key of wrong size."
        self._s = key
        self._t = [d - t for t in taps]

    def _sum(self, L):
        s = 0
        for x in L:
            s ^= x
        return s

    def _clock(self):
        b = self._s[0]
        self._s = self._s[1:] + [self._sum(self._s[p] for p in self._t)]
        return b

    def getbit(self):
        return self._clock()

class Geffe:
    def __init__(self, keyF, keyS, keyT):
        assert len(keyF) + len(keyS) + len(keyT) <= 19 + 23 + 27 # shard up 69+ bit key for 3 separate lfsrs
        # key = [int(i) for i in list("{:069b}".format(key))] # convert int to list of bits
        self.LFSR = [
            LFSR(keyF, [19, 18, 17, 14]),
            LFSR(keyS, [27, 26, 25, 22]),
            LFSR(keyT, [23, 22, 20, 18]),
        ]

    def getbit(self):
        b = [lfsr.getbit() for lfsr in self.LFSR]
        return b[1] if b[0] else b[2]


# The correlation method deploy by Geffe is highly vulnerablie to correlation attack.
# 75% matching

originalOutput = [0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1]

# # Brute force second LFSR with key size of 27 bit
# print("Breaking Second LFSR....")
# cand_key_4_sec_lfsr = []

# for flip in range(8):

#     for comb in tqdm(combinations(range(27), flip)):
#         key = [1 - originalOutput[i] if i in comb else originalOutput[i] for i in range(27)]
#         lfsr = LFSR(key, [27, 26, 25, 22])

#         counter = 0
#         for j in range(256):
#             if 256 - j + counter < 192:
#                 break
#             if originalOutput[j] == lfsr.getbit():
#                 counter += 1
        
#         if counter >= 180:
#             cand_key_4_sec_lfsr.append(key)
#             print(key)

# print(cand_key_4_sec_lfsr)

# print("Breaking Third LFSR")
# cand_key_4_third_lfsr = []

# for flip in range(7):

#     for comb in tqdm(combinations(range(23), flip)):
#         key = [1 - originalOutput[i] if i in comb else originalOutput[i] for i in range(23)]
#         lfsr = LFSR(key, [23, 22, 20, 18])

#         counter = 0
#         for j in range(256):
#             if 256 - j + counter < 192:
#                 break
#             if originalOutput[j] == lfsr.getbit():
#                 counter += 1
        
#         if counter >= 180:
#             cand_key_4_third_lfsr.append(key)
#             print(key)

# print(cand_key_4_third_lfsr)

# OMG it's so lucky we only got one shot
# Test First Key
secondKey = [0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1]
thirdKey =  [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1]

# HandCraft
#            0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1
defaultFirstKey = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0]

# hasDone = False
# for flip in range(10):

#     for comb in tqdm(combinations(range(19), flip)):
#         key = [1 - defaultFirstKey[i] if i in comb else defaultFirstKey[i] for i in range(19)]
#         lfsr = Geffe(key, secondKey, thirdKey)
#         failed = False

#         for j in range(256):
#             if originalOutput[j] != lfsr.getbit():
#                 failed = True
#                 break
        
#         if failed:
#             continue
#         else:
#             print(key)
#             hasDone = True
#             break
    
#     if hasDone:
#         break

FirstKey = [1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]

finalKey = int("".join([str(c) for c in FirstKey] + [str(c) for c in secondKey] + [str(c) for c in thirdKey]), 2)

ivh = "cd2832f408d1d973be28b66b133a0b5f"
enc_flag = "1e3c272c4d9693580659218739e9adace2c5daf98062cf892cf6a9d0fc465671f8cd70a139b384836637c131217643c1"

def decrypt_flag(key):
    sha1 = hashlib.sha1()
    sha1.update(str(key).encode('ascii'))
    key = sha1.digest()[:16]
    iv = bytes.fromhex(ivh)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(bytes.fromhex(enc_flag)), 16)
    
    print(plaintext)

decrypt_flag(finalKey)