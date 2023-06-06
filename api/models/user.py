# username, email, password, address, contact information, payment information
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Literal
import re
from html import escape

class User(BaseModel):
    id: Optional[str] = None
    first_name: str = Field(max_length=50, min_length=1, regex=r'^[a-zA-Z\s]+$')
    surname: str = Field(max_length=50, min_length=1, regex=r'^[a-zA-Z\s]+$')
    email: EmailStr
    country: str = Field(max_length=50, min_length=2, regex=r'^[a-zA-Z\s]+$')
    address: str = Field(max_length=300, min_length=1)
    cellphone: str = Field(..., min_length=9, max_length=15, regex=r"^\+?[0-9]{9,15}$")    

    @validator('address')
    def validate_address(cls, address):
        #Validate html and url. 
        patterns = [r'<(\/*?)(?!(em|p|br\s*\/|strong))\w+?.+?>',r'^(http|https):\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(\/\S*)?$']
        for pattern in patterns:
            if re.match(pattern, address):                        
                raise ValueError("Please put a valid address.")

        return address
    
    @validator('*', pre=True)
    def validate_xss(cls, value):
        if isinstance(value, str):
            escaped_value = escape(value)
            if escaped_value != value:
                raise ValueError("The field contains HTML or JavaScript code that is not allowed.")
        return value
            
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
    password: str = Field(max_length=300, min_length=1)
    role: Literal["user", "admin"] = "user"

    @validator('password')
    def validate_address(cls, password):
        #Validate html and url. 
        patterns = [r'<(\/*?)(?!(em|p|br\s*\/|strong))\w+?.+?>',r'^(http|https):\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(\/\S*)?$']
        for pattern in patterns:
            if re.match(pattern, password):                        
                raise ValueError("Please put a valid password.")
        
        pattern = r'^[a-zA-Z0-9_\-.$/]+$'
        if not re.match(pattern, password):
            raise ValueError("The password can only have special characters such as: _ o - ")
        return password            

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
        
# This class verify all the fields for a user, but when we want to update an user, we need that the field are optional. 
class UpdateUserSchema(UserDb):    
    first_name: Optional[str] = Field(None, max_length=50, min_length=1, regex=r'^[a-zA-Z\s]+$')
    surname: Optional[str]  = Field(None, max_length=50, min_length=1, regex=r'^[a-zA-Z\s]+$')
    email: Optional[EmailStr]
    country: Optional[str]  =  Field(None, max_length=50, min_length=2, regex=r'^[a-zA-Z\s]+$')
    address: Optional[str]  =  Field(None, max_length=300, min_length=1)
    cellphone: Optional[str]  =  Field(None, min_length=9, max_length=15, regex=r"^\+?[0-9]{9,15}$")
    password: Optional[str] = Field(None, max_length=300, min_length=1)
    role: Optional[Literal["user", "admin"]] = "user"    
