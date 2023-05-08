# username, email, password, address, contact information, payment information
from pydantic import BaseModel, Field
from typing import Optional, List


class User(BaseModel):
    id: Optional[str] = None
    first_name: str = Field(max_length=50, min_length=1)
    surname: str = Field(max_length=50, min_length=1)
    email: str = Field(max_length=300, min_length=1)
    country: str = Field(max_length=50, min_length=2)
    address: str = Field(max_length=300, min_length=1)
    cellphone: str = Field(max_length=14, min_length=10)
    # isVIP: Optional[str] = ("False",)
    # role: Optional[str] = "User"

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


class UserDb(User):    
    password: str = Field(max_length=30, min_length=1)
    role: Optional[str] = "user"
    
    # isVIP: Optional[str] = ("False",)

    class Config:
        schema_extra = {"example": {
            "first_name": "Juan Diego",
            "surname": "Bermudez Castaneda",
            "email": "juan.bermudez@onlineshop.com",
            "country": "Colombia",
            "password": "secret",            
            "address": "Av 123 #45-6, Medellín, Colombia",
            "cellphone": "+573002827310",
        }}
