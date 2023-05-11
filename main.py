from fastapi import FastAPI, Request, HTTPException
from api.routers.products import product_router
from api.routers.users import users_router
from api.routers.token import token_router

# from api.routers.users import auth_router
# from routers.vip_products import vip_products_router
# from routers.auth_forms import auth_router_forms
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from api.models.product import Product
# from db.database import db_client
# from bson import ObjectId
# from typing import List  # Response model
# from schemas.product import products_schema


app = FastAPI()
app.title = "Online Shop Project"
app.version = "0.0.1"
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
# Routers.
app.include_router(router=product_router)
app.include_router(router=users_router)
app.include_router(router=token_router)
# app.include_router(router=vip_products_router)
# app.include_router(router=auth_router_forms)


@app.get("/")
async def index(request: Request):
    # search in the data base and return the products
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context=context)
