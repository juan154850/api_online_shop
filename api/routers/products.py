from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from bson import ObjectId
from api.models.product import Product, ProductDataBase
from api.database import DataBase
from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument

import os


product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"message": "Page not found"}},
)

URI = os.getenv("URI")
db_client = DataBase(URI=URI, server_api=ServerApi("1")).db_client


@product_router.get("", status_code=status.HTTP_200_OK, response_model=List[ProductDataBase], response_class=JSONResponse)
async def get_products() -> List[ProductDataBase]:

    all_products = ProductDataBase.products_schema(
        self=ProductDataBase, product_list=db_client.db_products.products.find())
    return JSONResponse(content=all_products, status_code=200)


@product_router.get("/{key}", response_model=List[Product], status_code=status.HTTP_200_OK, response_class=JSONResponse)
async def get_product(key: str, value: str) -> List[Product]:
    if key == "id":
        product = Product.products_schema(
            self=Product, product_list=db_client.db_products.products.find({"_id": ObjectId(value)}))
        if (len(product) > 0):
            return JSONResponse(
                content=Product.products_schema(
                    self=Product, product_list=db_client.db_products.products.find({"_id": ObjectId(value)})),
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=404, detail="The product does not exists.")

    else:
        all_products_by_field = Product.products_schema(
            self=Product, product_list=db_client.db_products.products.find({key: value}))
    if len(all_products_by_field) > 0:
        return JSONResponse(content=all_products_by_field, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=404, detail="The product does not exists.")


@product_router.post("", status_code=status.HTTP_201_CREATED, response_model=Product)
async def create_product(product: Product) -> Product:
    product_dict = dict(product)
    id = db_client.db_products.products.insert_one(product_dict).inserted_id
    new_product = Product.product_schema(
        product=db_client.db_products.products.find_one({"_id": id}))
    return JSONResponse(content=new_product, status_code=status.HTTP_201_CREATED)


@product_router.patch("/{product_id}", status_code=200, response_class=JSONResponse, response_model=Product)
async def update_product(product_id: str, key: str, value: str | int) -> Product:
    product = (db_client.db_products.products.find_one(
        filter={"_id": ObjectId(product_id)}))
    if (type(product) == type(dict())):

        if (not product.get(key)):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid key")
        else:
            if (key == "amount" and value.isdigit()):
                value = int(value)
                new_product = Product.product_schema(db_client.db_products.products.find_one_and_update(
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
                    new_product = Product.product_schema(db_client.db_products.products.find_one_and_update(
                        filter={"_id": ObjectId(product_id)}, update={"$set": {key: value}}, return_document=ReturnDocument.AFTER))
                    return JSONResponse(content=new_product, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(404, detail="The product does not exists...")


@product_router.put("/{product_id}", response_class=JSONResponse, response_model=Product)
async def update_product(product_id: str, new_product: Product) -> Product:
    product = (db_client.db_products.products.find_one(
        filter={"_id": ObjectId(product_id)}))
    if (type(product) == type(dict())):
        # The product exists in the database and we can update all the product
        new_product_dict = dict(new_product)
        result = Product.product_schema(db_client.db_products.products.find_one_and_replace(
            filter={"_id": ObjectId(product_id)}, replacement=new_product_dict, return_document=ReturnDocument.AFTER))
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(404, detail="The product does not exists...")


@product_router.delete("/{product_id}")
async def delete_product(product_id: str):
    product = (db_client.db_products.products.find_one(
        filter={"_id": ObjectId(product_id)}))
    if (type(product) == type(dict())):
        db_client.db_products.products.find_one_and_delete(
            filter={"_id": ObjectId(product_id)})
        return JSONResponse(content={"Message": "Product deleted."}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(404, detail="The product does not exists...")
