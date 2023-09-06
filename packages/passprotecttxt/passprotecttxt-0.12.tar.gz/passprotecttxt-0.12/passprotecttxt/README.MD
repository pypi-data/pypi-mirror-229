# protects a text with a password 

## pip install passprotecttxt

#### Tested against Windows 10 / Python 3.10 / Anaconda 

### Encryption: 

The encrypt_text function provides a simple and secure way to encrypt text using AES encryption with CTR mode. AES is a widely used encryption algorithm known for its security and efficiency. CTR mode provides confidentiality and allows random access to the encrypted data.

### Decryption: 

The decrypt_text function complements the encryption process by decrypting the ciphertext back to its original plaintext form. It ensures that only authorized parties with the correct password can access and decrypt the data.


## copy & paste example

	
```python
from passprotecttxt import encrypt_text,decrypt_text

plaintext = "Hello, World!"
password = "MySecretPassword"

encrypted_text = encrypt_text(plaintext, password)
decrypted_text = decrypt_text(encrypted_text, password)

print("Plaintext:", plaintext)
print("Encrypted text:", encrypted_text)
print("Decrypted text:", decrypted_text)



# output

Plaintext: Hello, World!
Encrypted text: 63F720AC7E1F72B460271B2368
Decrypted text: Hello, World!



```