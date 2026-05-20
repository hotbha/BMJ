import bcrypt
hash = bcrypt.hashpw(b'Test@1234', bcrypt.gensalt()).decode()
print(hash)
