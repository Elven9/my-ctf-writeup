# 0x03 Reverse

## Lab - Baby

Open IDA, u will find the output position of the file `/tmp/baby_aksgmsdkvmdfiivjdd`, b4 xor-ed string `NotFLAG{Hello_Baby_Reverser}`, xor key

## Lab - List

After reverse the binary, the final result is simply two result xored together.

```txt
Value A: 0x4020 (dw) ^ 0x5A
Value B: 0x40A0 (dw) ^ 0xA5

result: value_a ^ value_b
```

Flag: `FLAG{alspdlp12lflasplkv0923kf01}`

## Lab - Main1


