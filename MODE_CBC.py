OMAC_CONSTS = {8 : 0x1B.to_bytes(8), 16 : 0x87.to_bytes(16), 32 : 0x425.to_bytes(32)} # NIST recomended

def bytes_left_bit_shift(orig_bytes: bytes, shift: int) -> bytes:
    return int.to_bytes((int.from_bytes(orig_bytes) << shift) % 2**(len(orig_bytes) * 8), len(orig_bytes))

def msb(byte):
    binary_representation = bin(byte)[2:].zfill(8)
    msb = int(binary_representation[0])
    return msb

def xor_bytes(bytes1: bytes, bytes2: bytes) -> bytes:
    return bytes(x^y for x,y in zip(bytes1, bytes2))

def generate_subkeys(cipher: object, block_len: int):
    L = cipher.encryption(b'\x00' * block_len)
    if msb(L[0]) == 0: k1 = bytes_left_bit_shift(L, 1)
    else: k1 = xor_bytes(bytes_left_bit_shift(L, 1), OMAC_CONSTS[block_len])
    if msb(k1[0]) == 0: k2 = bytes_left_bit_shift(k1, 1)
    else: k2 = xor_bytes(bytes_left_bit_shift(k1, 1), OMAC_CONSTS[block_len])
    return k1, k2

def encrypt(cipher: object, plain_text: bytes, iv: bytes, digest: bool = False):
    block_len = len(iv)
    assert len(plain_text) % block_len == 0
    enc_blocks: [bytes] = []
    enc_blocks.append(xor_bytes(plain_text[:block_len], iv))
    for i in range(block_len, len(plain_text), block_len):
        enc_blocks[-1] = cipher.encryption(enc_blocks[-1])
        enc_blocks.append(xor_bytes(plain_text[i:i+block_len], enc_blocks[-1]))
    enc_blocks[-1] = cipher.encryption(enc_blocks[-1])
    if not digest: return b''.join(enc_blocks)
    k1, _ = generate_subkeys(cipher, block_len)
    tag = cipher.encryption(xor_bytes(xor_bytes(plain_text[-block_len:], k1), enc_blocks[-2]))
    return b''.join(enc_blocks), tag

def decrypt(cipher: object, enc_text: bytes, iv: bytes, tag: bytes = None):
    block_len = len(iv)
    assert len(enc_text) % block_len == 0
    dec_blocks: [bytes] = []
    enc_blocks = [enc_text[i:i+block_len] for i in range(0,len(enc_text), block_len)]
    dec_blocks.append(xor_bytes(cipher.decryption(enc_blocks[0]), iv))
    for i in range(1, len(enc_blocks)):
        dec_blocks.append(xor_bytes(enc_blocks[i-1], cipher.decryption(enc_blocks[i])))
    if tag is None: return b''.join(dec_blocks)
    k1, _ = generate_subkeys(cipher, block_len)
    calculated_tag = cipher.encryption(xor_bytes(xor_bytes(dec_blocks[-1], k1), enc_blocks[-2]))
    if tag != calculated_tag: raise ValueError("MAC check failed")
    return b''.join(dec_blocks)