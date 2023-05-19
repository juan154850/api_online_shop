from fastapi import Response
from pydantic import BaseModel
from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
from api.database import DataBase
import time


import os

from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

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
        user = db.get("db_users","users","email",email)        
        if not user:
            return False
        if not self.verify_password(password, user["password"]):
            return False
        return user    
    
    def update_token(token: str):
        decoded_token = jwt.decode(token,SECRET_KEY,ALGORITHM)
        current_time = int(time.time())
        expiration_time = decoded_token['exp']        
        time_left = expiration_time - current_time        
        if time_left < 300: # less than 5 minutes left
            new_expiration_time = expiration_time + 300 # add 5 minutes
            new_token = jwt.encode({**decoded_token, 'exp': new_expiration_time}, SECRET_KEY, algorithm=ALGORITHM)            
            return new_token
        else:
            return token



class TokenData(BaseModel):
    email: str | None = None