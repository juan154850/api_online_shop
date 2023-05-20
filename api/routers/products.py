from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse

from typing import List
from bson import ObjectId

from api.models.product import Product, ProductDataBase
from api.database import DataBase
from api.routers.token import oauth2_scheme
from api.models.token import SECRET_KEY , ALGORITHM


from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument

from jose import jwt

import re

from dotenv import load_dotenv
load_dotenv()
import os




product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"message": "Page not found"}},
)

URI = os.getenv("URI")
db_client = DataBase(URI=URI, server_api=ServerApi("1"))


@product_router.get("", status_code=status.HTTP_200_OK, response_model=List[ProductDataBase], response_class=JSONResponse)
async def get_products() -> List[ProductDataBase]:

    all_products = ProductDataBase.products_schema(
        self=ProductDataBase, product_list=db_client.db_client.db_products.products.find())
    
    return JSONResponse(content=all_products, status_code=200)


@product_router.get("/{key}", response_model=List[Product], status_code=status.HTTP_200_OK, response_class=JSONResponse)
async def get_product(key: str, value: str) -> List[Product]:
    if key == "id":
        product = Product.products_schema(
            self=Product, product_list=db_client.db_client.db_products.products.find({"_id": ObjectId(value)}))
        if (len(product) > 0):
            return JSONResponse(
                content=Product.products_schema(
                    self=Product, product_list=db_client.db_client.db_products.products.find({"_id": ObjectId(value)})),
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=404, detail="The product does not exists.")

    else:
        all_products_by_field = Product.products_schema(
            self=Product, product_list=db_client.db_client.db_products.products.find({key: value}))
    if len(all_products_by_field) > 0:
        return JSONResponse(content=all_products_by_field, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=404, detail="The product does not exists.")


@product_router.post("", status_code=status.HTTP_201_CREATED, response_model=Product)
async def create_product(product: Product, token: str = Depends(oauth2_scheme)) -> Product:    

    error = "Internal server error, please report the problem with an administrator."
    try:
        # Decode the token.
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)        
        user = db_client.get("db_users", "users", "email", token["sub"])    
        if(type(user) != type (bool)):
            # The user exist.
            if(user["role"].lower() == "admin"):
                # Validate and create the product.            
                all_products = ProductDataBase.products_schema(
                    self=ProductDataBase, product_list=db_client.db_client.db_products.products.find())
                
                if (len(all_products) >= 50):
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail={"Message":"Database full."})

                product_dict = dict(product)
                id = db_client.db_client.db_products.products.insert_one(product_dict).inserted_id
                new_product = Product.product_schema(
                    product=db_client.db_client.db_products.products.find_one({"_id": id}))
                return JSONResponse(content=new_product, status_code=status.HTTP_201_CREATED)
            else:
                error = "you don't authorize for this action."
                raise error
        else:
            # the user does not exist
            error = "This user does not exist."
            raise error
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)





@product_router.patch("/{product_id}", status_code=200, response_class=JSONResponse, response_model=Product)
async def update_product(product_id: str, key: str, value: str | int) -> Product:
    product = (db_client.db_client.db_products.products.find_one(
        filter={"_id": ObjectId(product_id)}))
    if (type(product) == type(dict())):

        if (not product.get(key)):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid key")
        else:
            if (key == "amount" and value.isdigit()):
                value = int(value)
                new_product = Product.product_schema(db_client.db_client.db_products.products.find_one_and_update(
                    filter={"_id": ObjectId(product_id)}, update={"$set": {key: value}}, return_document=ReturnDocument.AFTER))
                return JSONResponse(content=new_product, status_code=status.HTTP_200_OK)
            else:
                if (key == "_id"):
                    raise HTTPException(
                        401, detail={"Message": "This key cannot be modified."})
                elif key == "amount":
                    raise HTTPException(
                        401, detail={"Message": "The value is not a number."})
                else:
                    new_product = Product.product_schema(db_client.db_client.db_products.products.find_one_and_update(
                        filter={"_id": ObjectId(product_id)}, update={"$set": {key: value}}, return_document=ReturnDocument.AFTER))
                    return JSONResponse(content=new_product, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(404, detail="The product does not exists...")


@product_router.put("/{product_id}", response_class=JSONResponse, response_model=Product)
async def update_product(product_id: str, new_product: dict, token:str = Depends(oauth2_scheme)) -> Product:

    error = "Internal server error, please report the bug and contact with an administrator."
    
    try:

        if( not (new_product) ):
            error = "The body can't be empty"
            raise error 

        # Validate the token.
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user = db_client.get("db_users", "users", "email", token["sub"])

        if (type(user) != type(bool)):
            # The user exist.
            if (user["role"].lower() == "admin"):
                # We can update the product.
                actual_product = db_client.get("db_products", "products", "_id", ObjectId(product_id))
                if (type(actual_product) == type(dict())):
                    # The product exists in the database and we can update all the product      
                                             
                    for key in new_product:                                
                        if (not (key in actual_product)):                            
                            error = f"The key: '{key}' don't exist."
                            raise error                              
                                                 
                        # if((not actual_product.get(key))):
                        if(  ((key == "amount") and ( not isinstance(new_product[key], int) )) ):   
                            error = "Invalid value for key: 'amount', please put an integer value."
                            raise error       
                        
                        
                        if (key == "price"):
                            patron = r'^\$([0-9]{1,3}(\,[0-9]{3})*|([0-9]+))(\.[0-9]{2})?$'
                            if not (re.match(patron, new_product["price"])):
                                # the value is incorrect.
                                error = f"Invalid value for the key: '{key}'. Please put a valid value in dollars."
                                raise error   
                        if( key == "image" ):
                            patron = r'^https:\/\/.*\.png$'
                            if not (re.match(patron, new_product["image"])):
                                error = f"Invalid value for the key: '{key}'. Please put a valid value for an image."
                                raise error   
                        if ( key == "_id" ):
                            error = f"The key: '{key}' can't be edit."
                            raise error
                        if( key == "name" ):                            
                            # html, url, phone, dni, price.
                            url_validations = [r'^(http|https):\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(\/\S*)?$', r'^\+\d{1,3}\s?\(\d{1,3}\)\s?\d{3}\-\d{4}$', r'^\d{8}$', r'^\$([0-9]{1,3}(\,[0-9]{3})*|([0-9]+))(\.[0-9]{2})?$', r'<[^>]+>']
                            for value in url_validations:
                                if re.match(value, new_product["name"]):
                                    error = f"The value: '{new_product.get('name')}' in the key: '{key}' are invalid."
                                    raise error
                                                                                 
                    # end for 
                    result = db_client.db_client.db_products.products.find_one_and_update({'_id': ObjectId(product_id)}, {'$set': new_product}, return_document=ReturnDocument.AFTER)                     
                    return JSONResponse(content=ProductDataBase.product_schema(result), status_code=status.HTTP_200_OK)
                    
                else:
                    error = f"The product with id: {product_id} does not exists..."
                    raise error
            else:
                error = "You don't authorize for this action."
                raise error
        else:
            error = "This user does not exist."
            raise error
    except:
        raise HTTPException(400, error)




@product_router.delete("/{product_id}")
async def delete_product(product_id: str, token: str = Depends(oauth2_scheme)):
    
    error = "Internal server error, please report the bug and contact with an administrator."
    try:
        # Validate the token.
        token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user = db_client.get("db_users", "users", "email", token["sub"])

        if( type(user) != type( bool ) ): 
            # The user exist. 
            if ( user["role"].lower() == "admin" ):
                # The user is admin and we can delete the product. 
                product = (db_client.db_client.db_products.products.find_one(
                filter={"_id": ObjectId(product_id)}))
                if (type(product) == type(dict())):
                    db_client.db_client.db_products.products.find_one_and_delete(
                        filter={"_id": ObjectId(product_id)})
                    return JSONResponse(content={"Message": "Product deleted."}, status_code=status.HTTP_200_OK)
                else:
                    error = "This product does not exist..." 
                    raise error
            else:
                error = "You don't authorize for this action."
                raise error
        else:
            # the user does not exists.
            error = "This user does not exist."
            raise error
    except:
        raise HTTPException(400, error)
    

