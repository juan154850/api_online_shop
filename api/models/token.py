from pydantic import BaseModel
from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
from api.database import DataBase

import os

from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class Token(BaseModel):
    access_token: str
    token_type: str

    # token = Token.create_access_token(data={"sub":user["email"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()    
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=1)
        to_encode.update({"exp": expire})    
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)    
        return encoded_jwt
    
    # token.verify_password("123456","$2b$12$ZLKSnTjGmdNdseQerw.Ou.vInH5PY2WRXInQuG3zJBRzWJyJabcSS")
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    # token.authenticate_user(token, db_client, "juan.bermudez@onlineshop.com", "123456")
    def authenticate_user(self, db: DataBase, email: str, password: str):
        user = db.get_user("db_users","users","email",email)        
        if not user:
            return False
        if not self.verify_password(password, user["password"]):
            return False
        return user


class TokenData(BaseModel):
    username: str | None = None