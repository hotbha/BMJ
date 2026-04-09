import bcrypt
password = "testpass123"
hash_value = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
print(hash_value.decode('utf-8'))
