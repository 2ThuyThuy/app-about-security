
from pydoc import plain
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

key = b'mysecretpassword'
# mã hóa
cipher = AES.new(key,AES.MODE_CBC)
nonce = cipher.nonce
plaintext = b'hide text'
ciphertext = cipher.encrypt(pad(plaintext,AES.block_size))

# giải mã
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
plaintext = cipher.decrypt(ciphertext)
print(plaintext)
