from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from Schemas.order import orderEntity, ordersEntity
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import OrderInfo, TokenInfo
from core.logger import log_user_action, log_system_event, log_error
from core.email_utils import send_order_confirmation_email


orders_router = APIRouter(prefix="/orders")


class OrderStatusUpdate(BaseModel):
    status: str


@orders_router.get("", status_code=status.HTTP_200_OK)
async def get_orders():
    try:
        log_system_event("GET_ALL_ORDERS", "Request to get all orders")
        orders = ordersEntity(db.orders.find())
        log_system_event("GET_ALL_ORDERS", f"Successfully retrieved {len(orders)} orders")
        return orders
    except Exception as e:
        log_error(e, "GET_ALL_ORDERS")
        raise

@orders_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_order_by_id(id: str, request: Request):
    try:
        log_system_event("GET_ORDER_BY_ID", f"Request to get order with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("GET_ORDER_BY_ID", f"Invalid order ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    order = db.orders.find_one({"_id": object_id})
    
    if order is None:
        log_system_event("GET_ORDER_BY_ID", f"Order not found with ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    order_data = orderEntity(order)
    log_system_event("GET_ORDER_BY_ID", f"Successfully retrieved order: {order_data.get('auto_name', 'Unknown')}")
    return order_data

@orders_router.get("/fromid/{id}", status_code=status.HTTP_200_OK)
async def get_order_by_from_id(id: str, request: Request):
    try:
        log_user_action("GET_ORDERS_BY_USER", user_id=id, details=f"Request to get orders for user ID: {id}")
        # Ищем все заказы по from_id
        orders = list(db.orders.find({"from_id": id}))
        
        if not orders:
            log_system_event("GET_ORDERS_BY_USER", f"No orders found for user ID: {id}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orders not found"
            )
        
        # Возвращаем список заказов
        orders_data = ordersEntity(orders)
        log_user_action("GET_ORDERS_BY_USER", user_id=id, details=f"Successfully retrieved {len(orders_data)} orders")
        return orders_data
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"GET_ORDERS_BY_USER - User ID: {id}")
        raise


@orders_router.post("/add_order", status_code=status.HTTP_201_CREATED)
async def add_user(order:OrderInfo):
    try:
        order_data = order.model_dump()
        log_user_action("CREATE_ORDER", user_id=order_data.get("from_id"), 
                      details=f"Creating new order for car: {order_data.get('auto_name', 'Unknown')}")
        
        result = db.orders.insert_one(
            {
                "from_id": order_data["from_id"],
                "email":order_data["email"],
                "name": order_data["name"],
                "auto_name": order_data["auto_name"],
                "number": order_data["number"],
                "comment": order_data["comment"],
                "status": order_data["status"],
             }
                            )
        
        log_user_action("CREATE_ORDER", user_id=order_data.get("from_id"), 
                       details=f"Successfully created order: {order_data.get('auto_name', 'Unknown')} (Order ID: {result.inserted_id})")
        
        # Отправляем email с подтверждением заказа
        email_sent = send_order_confirmation_email(
            to_email=order_data.get("email"),
            order_data=order_data
        )
        
        if not email_sent:
            log_system_event("CREATE_ORDER", f"Failed to send confirmation email to {order_data.get('email')}", "WARNING")
        
        return {"message": "Order created successfully", "id": str(result.inserted_id), "auto_name": order_data.get("auto_name")}
    except Exception as e:
        log_error(e, f"CREATE_ORDER - User ID: {order_data.get('from_id', 'Unknown')}")
        raise


@orders_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_order_by_id(id: str):
    try:
        log_user_action("DELETE_ORDER", details=f"Attempting to delete order with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("DELETE_ORDER", f"Invalid order ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    order = db.orders.find_one({"_id": object_id})
    
    if order is None:
        log_system_event("DELETE_ORDER", f"Order not found with ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order_auto_name = order.get("auto_name", "Unknown")
    order_from_id = order.get("from_id", "Unknown")
    
    result = db.orders.delete_one({"_id": object_id})
    
    if result.deleted_count == 1:
        log_user_action("DELETE_ORDER", user_id=order_from_id, 
                       details=f"Successfully deleted order: {order_auto_name} (ID: {id})")
        return {"message": "Order deleted successfully", "id": id}
    else:
        log_system_event("DELETE_ORDER", f"Failed to delete order with ID: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        )


@orders_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_order_status(id: str, order_update: OrderStatusUpdate):
    try:
        log_user_action("UPDATE_ORDER_STATUS", details=f"Attempting to update order status with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("UPDATE_ORDER_STATUS", f"Invalid order ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    order = db.orders.find_one({"_id": object_id})
    
    if order is None:
        log_system_event("UPDATE_ORDER_STATUS", f"Order not found with ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    old_status = order.get("status", "Unknown")
    new_status = order_update.status
    order_auto_name = order.get("auto_name", "Unknown")
    order_from_id = order.get("from_id", "Unknown")
    
    log_system_event("UPDATE_ORDER_STATUS", 
                    f"Updating order status from '{old_status}' to '{new_status}' for order ID: {id}")
    
    result = db.orders.update_one(
        {"_id": object_id},
        {"$set": {"status": new_status}}
    )
    
    if result.modified_count == 1:
        # Получаем обновленный документ
        updated_order = db.orders.find_one({"_id": object_id})
        order_data = orderEntity(updated_order)
        
        log_user_action("UPDATE_ORDER_STATUS", user_id=order_from_id, 
                       details=f"Successfully updated order status: {order_auto_name} (ID: {id}) from '{old_status}' to '{new_status}'")
        
        return order_data
    else:
        log_system_event("UPDATE_ORDER_STATUS", f"Failed to update order status with ID: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )
    