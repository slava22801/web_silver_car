def orderEntity(item) -> dict:
    order_dict = {
        "id":str(item["_id"]),
        "from_id":item["from_id"],
        "email":item["email"],
        "name":item["name"],
        "auto_name":item["auto_name"],
        "number":item["number"],
        "comment":item["comment"],
        "status":item["status"],
    }
    # Добавляем role, если оно есть в документе
    return order_dict

def ordersEntity(entity) -> list:
    return [orderEntity(item) for item in entity]