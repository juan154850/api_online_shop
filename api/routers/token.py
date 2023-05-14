from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from api.models.token import Token
from api.database import DataBase

from pymongo.server_api import ServerApi
from typing import Annotated
from datetime import timedelta

import os
from dotenv import load_dotenv
load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
token_router = APIRouter(tags=["Auth"], prefix="/auth")
URI = os.getenv("URI")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@token_router.post("", response_model=Token, response_class=JSONResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                response: Response):
    token = Token
    db = DataBase(URI, ServerApi("1"))
    user = Token.authenticate_user(
        token, db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = token.create_access_token(
        data={"sub": user["email"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)    
    return {"access_token": access_token, "token_type": "bearer"}
