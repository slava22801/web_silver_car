def carEntity(item) -> dict:
    return {
        "id":str(item["_id"]),
        "name":item["name"],
        "price":item["price"],
        "mileage":item["mileage"],
        "engine":item["engine"],
        "transmition_box":item["transmition_box"],
        "gear":item["gear"],
        "rudder":item["rudder"],
        "carcase":item["carcase"],
        "color":item["color"]
    }

def carsEntity(entity) -> list:
    return [carEntity(item) for item in entity]