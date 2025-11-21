from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from Schemas.review import reviewEntity, reviewsEntity
from Schemas.schemas import ReviewInfo
from database.db_init import db
from core.logger import log_system_event, log_error


reviews_router = APIRouter(prefix="/reviews")


@reviews_router.post("/add_review", status_code=status.HTTP_201_CREATED)
async def add_review(review: ReviewInfo):
    """
    Создает новый отзыв
    
    Args:
        review: Данные отзыва (name, email, rating, comment, consent)
    
    Returns:
        dict: Сообщение об успешном создании и ID отзыва
    """
    try:
        review_data = review.model_dump()
        
        # Валидация рейтинга (должен быть от 1 до 5)
        if review_data["rating"] < 1 or review_data["rating"] > 5:
            log_system_event("CREATE_REVIEW", f"Invalid rating value: {review_data['rating']}", "ERROR")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Проверка согласия на обработку данных
        if not review_data["consent"]:
            log_system_event("CREATE_REVIEW", f"Review rejected - no consent from {review_data.get('email', 'Unknown')}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consent is required to submit a review"
            )
        
        log_system_event("CREATE_REVIEW", f"Creating new review from {review_data.get('name', 'Unknown')} ({review_data.get('email', 'Unknown')})")
        
        # Добавляем дату создания
        review_document = {
            "name": review_data["name"],
            "email": review_data["email"],
            "rating": review_data["rating"],
            "comment": review_data["comment"],
            "consent": review_data["consent"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.reviews.insert_one(review_document)
        
        log_system_event("CREATE_REVIEW", 
                        f"Successfully created review from {review_data.get('name', 'Unknown')} "
                        f"(Review ID: {result.inserted_id}, Rating: {review_data.get('rating')})")
        
        return {
            "message": "Review created successfully",
            "id": str(result.inserted_id),
            "name": review_data.get("name")
        }
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"CREATE_REVIEW - Email: {review_data.get('email', 'Unknown')}")
        raise


@reviews_router.get("", status_code=status.HTTP_200_OK)
async def get_reviews():
    """
    Получает все отзывы
    
    Returns:
        list: Список всех отзывов
    """
    try:
        log_system_event("GET_ALL_REVIEWS", "Request to get all reviews")
        reviews = reviewsEntity(db.reviews.find().sort("created_at", -1))  # Сортировка по дате (новые сначала)
        log_system_event("GET_ALL_REVIEWS", f"Successfully retrieved {len(reviews)} reviews")
        return reviews
    except Exception as e:
        log_error(e, "GET_ALL_REVIEWS")
        raise

