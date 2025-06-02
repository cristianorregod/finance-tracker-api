from models.user import User
from schemas.user import UserSchema
from utils.password_manager import PasswordManager


class UserService():

    def __init__(self, db):
        self.db = db

    def create_user(self, user: UserSchema):
        password_manager = PasswordManager()
        new_user = User(**user.dict())
        print("User",new_user)
        print("Original pass",new_user.password)
        new_user.password = password_manager.hash_password(new_user.password)
        self.db.add(new_user)
        self.db.commit()
        return new_user

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
