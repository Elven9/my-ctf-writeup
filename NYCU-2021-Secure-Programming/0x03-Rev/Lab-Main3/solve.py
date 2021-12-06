src_fname = [0x6B79663078747A34, 0x6B697184665A7168, 0x2A752B7E267D8378, 0x757D7E7C6D7E2E30, 0x460D5B584A4E564A, 0x524D49]
src_fname_len = [8, 8, 8, 8, 8, 4]

encode_fname = b"".join([src_fname[i].to_bytes(src_fname_len[i], 'little') for i in range(6)])

fname = ""

for i in range(0x2A+1):
    fname += chr((encode_fname[i]-5) ^ i)

print("File Name: " + fname)

