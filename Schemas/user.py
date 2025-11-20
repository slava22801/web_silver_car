def userEntity(item) -> dict:
    user_dict = {
        "id":str(item["_id"]),
        "name":item["username"],
        "email":item["email"],
        "role":item["role"]
    }
    # Добавляем role, если оно есть в документе
    return user_dict

def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]