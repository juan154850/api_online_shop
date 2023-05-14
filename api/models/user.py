# username, email, password, address, contact information, payment information
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
import re


class User(BaseModel):
    id: Optional[str] = None
    first_name: str = Field(max_length=50, min_length=1)
    surname: str = Field(max_length=50, min_length=1)
    email: EmailStr
    country: str = Field(max_length=50, min_length=2)
    address: str = Field(max_length=300, min_length=1)
    cellphone: str = Field(..., min_length=9, max_length=15, regex=r"^\+?[0-9]{9,15}$")    

    @staticmethod
    def user_schema(user: 'User') -> 'User':
        return {
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "surname": user["surname"],
            "email": user["email"],
            "country": user["country"],
            # "password": user["password"],
            # "role": user["role"],
            "address": user["address"],
            "cellphone": user["cellphone"]
        }

    def users_schema(self, users_list: List['User']) -> List['User']:
        return [
            self.user_schema(value) for value in users_list
        ]       
    
    def validate_email(email: str):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class UserDb(User):    
    password: str = Field(max_length=30, min_length=1)
    role: Literal["user", "admin"] = "user"

    
    # isVIP: Optional[str] = ("False",)

    class Config:
        schema_extra = {"example": {
            "first_name": "Juan Diego",
            "surname": "Bermudez Castaneda",
            "email": "juan.bermudez@onlineshop.com",
            "country": "Colombia",
            "password": "secret",            
            "address": "Av 123 #45-6, Medellín, Colombia",
            "cellphone": "+xxxxxxxxx",
        }}

    def is_admin(self):
        if (self.role.lower() == "admin"):
            return True
        else:
            return False
