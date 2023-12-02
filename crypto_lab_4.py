from gost import gost2015
from Crypto.Protocol.KDF import scrypt
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import random
plain_text_len = 2211


def encrypt(plain_text: bytes, key: bytes) -> bytes:
    password = input("password: ")
    salt = hex(random.getrandbits(64))[2:]
    plain_text = bytes.fromhex(input("plain text(hex): "))
    plain_text = open(input("plain text file: "), "rb").read()
    # Возьмём рекомендуемые параметры  (N=4096, r=32, p=1)
    # https://words.filippo.io/the-scrypt-parameters/ So the minimum memory requirement of scrypt is: 128 × 𝑁 × 𝑟 bytes
    # Значит расход памяти будет 128*5096*32 байт ~ 16 Мбайт
    key = scrypt(password=password, salt=salt, key_len=256, N = 4096, r = 32, p = 1)
    padded = pad(plain_text, block_size=16, style='pkcs7')




