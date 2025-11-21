def reviewEntity(item) -> dict:
    review_dict = {
        "id": str(item["_id"]),
        "name": item["name"],
        "email": item["email"],
        "rating": item["rating"],
        "comment": item["comment"],
        "consent": item["consent"],
    }
    # Добавляем дату создания, если она есть в документе
    if "created_at" in item:
        review_dict["created_at"] = item["created_at"]
    return review_dict

def reviewsEntity(entity) -> list:
    return [reviewEntity(item) for item in entity]

