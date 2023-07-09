from cryptography.fernet import Fernet


def encrypt(data):

    # Generate a new encryption key
    # key = Fernet.generate_key()
    #
    # # Store the encryption key securely (e.g., in a file or in a secret management service)
    # with open('key/encryption_key.key', 'wb') as key_file:
    #   key_file.write(key)

    with open('key/encryption_key.key', 'rb') as key_file:
        key = key_file.read()

    # Initialize the Fernet cipher with the encryption key
    cipher = Fernet(key)

    # Encrypt the data
    data = data.encode()
    encrypted_data = cipher.encrypt(data)

    return encrypted_data


def decrypt(data):
    with open('key/encryption_key.key', 'rb') as key_file:
        key = key_file.read()


    # Initialize the Fernet cipher with the encryption key
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    decrypt = decrypted_data.decode()
    return decrypt
