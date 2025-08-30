import bcrypt

def hash_password(plain: str) -> str:
    binary = plain.encode(encoding='utf-8')
    hashed_binary = bcrypt.hashpw(binary, 
                                  bcrypt.gensalt(rounds=12))
    return hashed_binary.decode(encoding='utf-8')



def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(encoding='utf-8'),
                          hashed.encode(encoding='utf-8'))