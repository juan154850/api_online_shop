from fastapi import APIRouter, status, HTTPException, Depends, Response
from fastapi.responses import JSONResponse

from api.models.user import User, UserDb
from api.database import DataBase
from api.models.token import Token

from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument

from typing import List
from passlib.context import CryptContext
from api.routers.token import oauth2_scheme
from jose import jwt

from bson import ObjectId

import os

from dotenv import load_dotenv
load_dotenv()


users_router = APIRouter(prefix="/users", tags=["Users"])


URI = os.getenv("URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

db_client = DataBase(URI, ServerApi("1"))

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


@users_router.get("", response_class=JSONResponse, response_model=User)
async def get_users(response: Response, token: str = Depends(oauth2_scheme)) -> List[User]:

    # error = "Internal server error, please report the bug with the administrator of the page."
    # try:

        # print(f"Actual token: {token}")
        # token = Token.update_token(token)             
        # print(f"Updated token: {token}")
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user = db_client.db_client.db_users.users.find_one(
            {"email": token["sub"]})
        if ((type(user) != None) and (user["role"].lower() == "admin")):
            all_users = User.users_schema(
                self=User, users_list=db_client.db_client.db_users.users.find())
            return JSONResponse(content=all_users, status_code=200)
        else:
            error = {"Message": "Not authorized"}
            raise error
    # except:
    #     raise HTTPException(status_code=400, detail=error)


@users_router.get("/{id}")
async def get_users(id: str, token: str = Depends(oauth2_scheme)):

    error = {"Message": "Error in except"}
    # token = Token.update_token(token)
    try:
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_token = db_client.db_client.db_users.users.find_one(
            {"email": token["sub"]})
        if (type(user_token) != type(None)):
            user = db_client.db_client.db_users.users.find_one(
                {"_id": ObjectId(id)})
            if (((type(user) != type(None)) and ((user_token["_id"] == user["_id"]))) or ((type(user) != type(None)) and (user_token["role"].lower() == "admin"))):
                return JSONResponse(content=User.user_schema(user), status_code=200)
            else:
                error = {
                    "Message": "The user does not exits or you don not authorized for this action."}
                raise error
    except:
        raise HTTPException(
            status_code=404, detail=error)


@users_router.post("/", response_class=JSONResponse, response_model=UserDb)
async def create_account(account: UserDb) -> UserDb:
    all_users = User.users_schema(
        self=User, users_list=db_client.db_client.db_users.users.find())

    if (len(all_users) >= 50):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail={
                            "Message": "Database full."})

    if (not (db_client.db_client.db_users.users.find_one(filter={"email": account.email}))):
        if (not (db_client.db_client.db_users.users.find_one(filter={"cellphone": account.cellphone}))):
            new_account = account.dict()
            if new_account["email"] == "juan.bermudez@onlineshop.com":
                new_account["role"] = "admin"
            else:
                new_account["role"] = "user"
            print(new_account["password"])
            new_account["password"] = crypt.hash(
                secret=new_account["password"])
            del new_account["id"]
            id = db_client.db_client.db_users.users.insert_one(
                new_account).inserted_id
            new_account = UserDb.user_schema(
                db_client.db_client.db_users.users.find_one(filter={"_id": id}))
            return JSONResponse(dict(new_account), status_code=201)
        else:
            raise HTTPException(404, "This cellphone already exists.")

    else:
        raise HTTPException(404, "This email already exists.")


@users_router.put("/{account_id}", response_class=JSONResponse, response_model=UserDb)
async def update_user(account_id: str, new_user: dict, token: str = Depends(oauth2_scheme)) -> UserDb:

    error = {
        "Message": "Internal server error, please contact and administrator and report the bug."}
    # token = Token.update_token(token)

    try:

        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_token = db_client.db_client.db_users.users.find_one(
            {"email": token["sub"]})

        if (type(user_token) != type(None)):
            user = db_client.db_client.db_users.users.find_one(
                {"_id": ObjectId(account_id)})
            if (((type(user) != type(None)) and ((user_token["_id"] == user["_id"]))) or ((type(user) != type(None)) and (user_token["role"].lower() == "admin"))):
                for key in new_user:
                    if (not user.get(key)):
                        error = {"Message": "Any key is invalid."}
                        raise error
                    if (key == "password"):
                        new_user["password"] = crypt.hash(
                            secret=new_user["password"])
                    if (key == "role" and user_token["role"].lower() != "admin"):
                        error = {"Message": "Not authorized"}
                        raise error
                    if ((key == "role") and (new_user["role"] not in ["user", "admin"])):
                        error = {"Message": "Invalid rol"}
                        raise error
                    if key == "email":
                        # validate if the email exist, if the email not exits, could can be use it.
                        search_email = db_client.db_client.db_users.users.find_one(
                            {"email": new_user["email"]})
                        if type(search_email) == type(None):
                            # The email is free
                            # Validate the structure of the email
                            is_a_valid_email = User.validate_email(
                                new_user["email"])
                            if not is_a_valid_email:
                                error = {"Message": "Invalid email"}
                                raise error
                        else:
                            error = {
                                "Message": "This email is already in use."}
                            raise error
                # end for
                temp_user = db_client.db_client.db_users.users.find_one(
                    {"_id": ObjectId(account_id)})
                print(temp_user)
                temp_user["email"] = new_user["email"]
                new_user = UserDb(**temp_user)
                print(new_user)
                updated_user = db_client.db_client.db_users.users.find_one_and_update(
                    {'_id': ObjectId(account_id)}, {'$set': new_user}, return_document=ReturnDocument.AFTER)
                return JSONResponse(content=UserDb.user_schema(updated_user))
            else:
                error = {
                    "Message": "The user does not exits or you don not authorized for this action."}
                raise error
        else:
            error = {"Message": "This user does not exist."}
            raise error
    except:
        # if we have an error, send the raise.
        raise HTTPException(406, detail=error)


@users_router.delete("/{account_id}")
async def delete_user(account_id: str, token: str = Depends(oauth2_scheme)):

    try:
        # token = Token.update_token(token)
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        if (type(db_client.db_client.db_users.users.find_one({"_id": ObjectId(account_id)})) != type(None)):

            user = db_client.db_client.db_users.users.find_one(
                {"email": token["sub"]})
            if ((type(user) != type(None)) and (user["role"].lower() == "admin")):

                db_client.db_client.db_users.users.find_one_and_delete(
                    filter={"_id": ObjectId(account_id)})
                return JSONResponse(content={"Message": "User deleted successfully"}, status_code=200)
            else:
                error = {"Message": "Not authorized"}
                raise error
        else:
            error = {"Message": "This user does not exist."}
            raise error
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error)
