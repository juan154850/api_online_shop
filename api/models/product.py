# id, name of the product, description, price, image, amount.
from pydantic import BaseModel, Field
from typing import Optional, List


class Product(BaseModel):
    # id: Optional[str] = None  # Optional field
    name: str = Field(max_length=100, min_length=1)
    price: str = Field(max_length=20, min_length=1)
    location: str = Field(max_length=50, min_length=1)
    image: str = Field(min_length=1, max_length=300)
    amount: int = Field(min_value=1, max_value=100)

    class Config:
        schema_extra = {
            "example": {
                # "id": "643b3d1e12ead7e70c5098e6",
                "name": "Name of the product",
                "price": "$Price",
                "location": "Location to sell the product",
                "image": "https://example.com.co",
                "amount": "0"
            }
        }

    @staticmethod
    def product_schema(product: 'Product') -> 'Product':
        return {
            "id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "location": product["location"],
            "image": product["image"],
            "amount": product["amount"]
        }

    def products_schema(self, product_list: List['Product']) -> List['Product']:
        return [
            self.product_schema(value) for value in product_list
        ]


class ProductDataBase(Product):

    id: Optional[str] = None  # Optional field
