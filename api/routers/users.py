from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from api.models.user import User, UserDb
from api.database import DataBase

from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument

from typing import List

from passlib.context import CryptContext

from bson import ObjectId

import os

from dotenv import load_dotenv
# load_dotenv()


# from fastapi import APIRouter, status, HTTPException, Depends, Form
# # from db.models.auth_model import User, UserDb
# # from db.database import db_client
# # from functions.auth_functions import search_user_db, current_user

# from bson import ObjectId
# from pymongo import ReturnDocument
# # from functions.vip_functions import is_admin
# from typing import Annotated


users_router = APIRouter(prefix="/users", tags=["Users"])


URI = os.getenv("URI")
SECRET_KEY = os.getenv("SECRET_KEY")
db_client = DataBase(URI, ServerApi("1")).db_client

crypt = CryptContext(schemes=["bcrypt"])
# crypt.

# #This method show the data.


@users_router.get("", response_class=JSONResponse, response_model=User)
async def get_users() -> List[User]:
    all_users = User.users_schema(
        self=User, users_list=db_client.db_users.users.find())
    return JSONResponse(content=all_users, status_code=200)


@users_router.get("/{key}")
async def get_users(key: str, value: str):
    try:
        if key == "id":
            user = User.users_schema(
                self=User, users_list=db_client.db_users.users.find({"_id": ObjectId(value)}))
            if (len(user) > 0):
                return JSONResponse(
                    content=User.users_schema(
                        self=User, users_list=db_client.db_users.users.find({"_id": ObjectId(value)})),
                    status_code=status.HTTP_200_OK
                )
        else:
            all_users_by_field = User.users_schema(
                self=User, users_list=db_client.db_users.users.find({key: value}))
            if len(all_users_by_field) > 0:
                return JSONResponse(content=all_users_by_field, status_code=status.HTTP_200_OK)
    except:
        raise HTTPException(
            status_code=404, detail="The user does not exists.")


@users_router.post("/", response_class=JSONResponse, response_model=UserDb)
async def create_account(account: UserDb) -> UserDb:

    all_users = User.users_schema(
        self=User, users_list=db_client.db_users.users.find())

    if (len(all_users) >= 50):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail={"Message":"Database full."})

    if (not (db_client.db_users.users.find_one(filter={"email": account.email}))):
        if (not (db_client.db_users.users.find_one(filter={"cellphone": account.cellphone}))):
            new_account = account.dict()
            if new_account["email"] == "juan.bermudez@onlineshop.com":
                new_account["role"] = "admin"
            else:
                new_account["role"] = "user"
            new_account["password"] = crypt.hash(secret=SECRET_KEY)
            del new_account["id"]
            id = db_client.db_users.users.insert_one(new_account).inserted_id
            new_account = UserDb.user_schema(
                db_client.db_users.users.find_one(filter={"_id": id}))
            return JSONResponse(dict(new_account), status_code=201)
        else:
            raise HTTPException(404, "This cellphone already exists.")

    else:
        raise HTTPException(404, "This email already exists.")
# Original
# @users_router.put("/{account_id}", response_class=JSONResponse, response_model=UserDb)
# async def update_user(account_id: str, new_user: dict) -> UserDb:        
#     try:
#         # Validate the item...        
#         if(type(db_client.db_users.users.find_one({"_id": ObjectId(account_id)})) != type(None)):                                    
#             actual_user = UserDb.user_schema(db_client.db_users.users.find_one({"_id":ObjectId(account_id)}))            
#             for key in new_user:                
#                 if( not actual_user.get(key)):
#                     error = {"Message":"Any key is invalid."}
#                     raise error
#             # end for

#             updated_user = db_client.db_users.users.find_one_and_update({'_id': ObjectId(account_id)}, {'$set': new_user}, return_document=ReturnDocument.AFTER)            
#             return JSONResponse(content=UserDb.user_schema(updated_user))
#         else:
#             error = {"Message":"This user does not exist."}
#             raise error
#     except:
#         # if we have an error, send the raise.
#         raise HTTPException(406, detail=error)     
    
# Test
@users_router.put("/{account_id}", response_class=JSONResponse, response_model=UserDb)
async def update_user(account_id: str, new_user: dict) -> UserDb:        
    try:
        # Validate the item...        
        if(type(db_client.db_users.users.find_one({"_id": ObjectId(account_id)})) != type(None)):                                    
            actual_user = (db_client.db_users.users.find_one({"_id":ObjectId(account_id)}))             
            for key in new_user:                
                if( not actual_user.get(key)):
                    error = {"Message":"Any key is invalid."}
                    raise error
                if(key == "password"):
                    new_user["password"] = crypt.hash(secret=SECRET_KEY)
            # end for            
            updated_user = db_client.db_users.users.find_one_and_update({'_id': ObjectId(account_id)}, {'$set': new_user}, return_document=ReturnDocument.AFTER)            
            return JSONResponse(content=UserDb.user_schema(updated_user))
        else:
            error = {"Message":"This user does not exist."}
            raise error
    except:
        # if we have an error, send the raise.
        raise HTTPException(406, detail=error)     


@users_router.delete("/{account_id}")
async def delete_user(account_id: str):
    try:
        if (type(db_client.db_users.users.find_one({"_id": ObjectId(account_id)})) != type(None)):
            print("The user exist.")
            db_client.db_users.users.find_one_and_delete(
                filter={"_id": ObjectId(account_id)})
            return JSONResponse(content={"Message": "User deleted successfully"}, status_code=200)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                "Message": "This user does not exist."})
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                            "Message": "This user does not exist."})


# @auth_router.post("")
# async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
#     user = search_user_db("email", username)
#     if (user):
#         #verify the password.
#         user_db = db_client.db_users.users.find_one({"email":user.email})
#         print(user_db["password"])
#         print(crypt.verify(secret="123456",hash=password))
#         #the users is valid and we can generate the token...
#         return JSONResponse(content="Login successfully")
#         # else:
#             #the password is not correct.
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The password are not correct.")
#     else:
#         print("This users does not exists.")
#     pass
