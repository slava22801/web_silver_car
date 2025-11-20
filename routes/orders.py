from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from Schemas.order import orderEntity, ordersEntity
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import OrderInfo, TokenInfo


orders_router = APIRouter(prefix="/orders")

@orders_router.get("")
async def get_orders():
    return ordersEntity(db.orders.find())

@orders_router.get("/{id}")
async def get_order_by_id(id: str, request: Request):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    order = db.orders.find_one({"_id": object_id})
    
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    order_data = orderEntity(order)
    
    return order_data

@orders_router.get("/fromid/{id}")
async def get_order_by_from_id(id: str, request: Request):
    # Ищем все заказы по from_id
    orders = list(db.orders.find({"from_id": id}))
    
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orders not found"
        )
    
    # Возвращаем список заказов
    return ordersEntity(orders)


@orders_router.post("/add_order")
async def add_user(order:OrderInfo):
    
    order_data = order.model_dump()
    
    
    db.orders.insert_one(
        {
            "from_id": order_data["from_id"],
            "name": order_data["name"],
            "auto_name": order_data["auto_name"],
            "number": order_data["number"],
            "comment": order_data["comment"],
         }
                        )
    