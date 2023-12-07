from gost import gost2015
cipher = gost2015(b'asdasdasdasdasdasdasdasdasdasdas')
enc = cipher.encryption(b'Hello, world!!!!')
print(enc)
dec = cipher.decryption(enc)
print(dec)