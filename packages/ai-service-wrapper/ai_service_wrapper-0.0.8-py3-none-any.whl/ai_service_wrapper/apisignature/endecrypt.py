import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def encrypt(payload, public_key=None, public_key_file='ENV/public.pem'):
    if not public_key:
        # Load the public key
        with open(public_key_file, 'rb') as file:
            public_key = serialization.load_pem_public_key(file.read())
    else:
        public_key = serialization.load_pem_public_key(
            bytes(public_key, 'utf-8'))

    # Encrypt the data
    encrypted_data = public_key.encrypt(
        payload,
        padding.PKCS1v15()
    )

    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt(base64encrypted_data, private_key=None, private_key_file='ENV/private.pem'):
    if not private_key:
        # Load the private key
        with open(private_key_file, 'rb') as file:
            private_key = serialization.load_pem_private_key(
                file.read(),
                password=None  # You might need to provide a password if the key is encrypted
            )
    else:
        private_key = serialization.load_pem_public_key(
            bytes(private_key, 'utf-8'))

    encrypted_data = base64.b64decode(base64encrypted_data)
    # Decrypt the data
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.PKCS1v15()
    )

    return decrypted_data.decode('utf-8')