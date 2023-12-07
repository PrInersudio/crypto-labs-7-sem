from Crypto.Protocol.KDF import scrypt
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import  get_random_bytes
from gost import gost2015
import MODE_CBC
block_len = 16
key_len = 32
plain_text_len = 2211
padded_text_len = plain_text_len + block_len - (plain_text_len % block_len)


def encrypt():
    password = input("password: ")
    salt = get_random_bytes(8)
    iv = get_random_bytes(block_len)
    plain_text = open(input("plain text file: "), "rb").read()
    assert len(plain_text) == plain_text_len
    # Возьмём параметры  (N=4096, r=32, p=1)
    # https://words.filippo.io/the-scrypt-parameters/ So the minimum memory requirement of scrypt is: 128 × 𝑁 × 𝑟 bytes
    # Значит расход памяти будет 128*4096*32 байт ~ 16 Мбайт
    key1, key2 = scrypt(password=password, salt=salt.hex(), key_len=key_len, N = 4096, r = 32, p = 1, num_keys=2)
    padded = pad(plain_text, block_size=block_len, style='pkcs7')
    encrypted, tag = MODE_CBC.encrypt(gost2015(key1), padded, iv, True)
    cipher_key2 = gost2015(key2)
    tag = cipher_key2.encryption(tag)
    open(input("message file: "), "wb").write(len(salt).to_bytes(1, "little") + salt + iv + encrypted + tag)


def decrypt():
    message = open(input("message file: "), "rb").read()
    salt_len = message[0]
    salt = message[1:salt_len+1]
    iv = message[salt_len+1:salt_len+1+block_len]
    encrypted = message[salt_len+1+block_len:salt_len+1+block_len+padded_text_len]
    tag = message[salt_len+1+block_len+padded_text_len:len(message)]
    password = input("password: ")
    key1, key2 = scrypt(password=password, salt=salt.hex(), key_len=key_len, N = 4096, r = 32, p = 1, num_keys=2)
    cipher_key2 = gost2015(key2)
    tag = cipher_key2.decryption(tag)
    encrypted = MODE_CBC.decrypt(gost2015(key1), encrypted, iv, tag)
    unpaded = unpad(encrypted, block_size=block_len, style='pkcs7')
    open(input("decrypted file: "), "wb").write(unpaded)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-m", "--mode", choices=["encryption", "decryption"], help="Choise mode", required=True)
    args = parser.parse_args()
    if args.mode == "encryption": encrypt()
    elif args.mode == "decryption": decrypt()
    else: print("WTF?")