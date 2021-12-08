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

Simple xor problem, the source code hide in the init_array, `0x11EA`, reverse that part and the flag will be recovered.

Flag: `FLAG{DK_ShowMaker_WWT}`

## Lab - Main2

Simple xor problem, ignore previous logic bomb, just straight to the important part at `0x125E`

Flag: `FLAG{Faker_BibleThump}`

## Lab - Main3

Two suspicious function at `.fini_array`, `0x12BA` and `0x11DE`.

`0x12BA` -> Open a File and Dup2
`0x11DE` -> Simple String Compare and write

Flag store at: `/tmp/drake_jsajicoj2m3f230cskdfoepkfws.flag`

Reverse Order?
![Oracle -Linker and Libraries Guide](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter3-8.html)

## Lab - Main4

Just like lab - main3, but in x86

Flag store at: `drake_vmimef283jfemkfms.flag`

## Lab - HelloWindows

NotFLAG{Windows_15_S0_GREAT_15NT_IT?}
FLAG

Substract with user input, xor with it, got the flag with x64dbg.

Flag: `FLAG{H3ll_W1nd0wS}`

## Lab - Traditional_GUI

account: 亞洲統神
password: toyz2k7e.3

`WinMain` is primary about creating the gui interface only. All logic is at call back function.

The big block of code is about drawing flag with raw line.

Flag: `FLAG{WIN32_GUI_SO_PAIN}`

## Lab - dll

First Number: 1418168133
Second Number: 1717982566

Flag: `FLAG{dLL_So_c00L_R1gHT?}`
