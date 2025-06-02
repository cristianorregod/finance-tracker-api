import bcrypt
class PasswordManager():
    def __init__(self):
        self.bcrypt = bcrypt

    def hash_password(self, password: str) -> str:
        return self.bcrypt.hashpw(password.encode('utf-8'), self.bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        return self.bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
