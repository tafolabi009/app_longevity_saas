from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json

from app_longevity_saas.backend.models.user import User, Prediction
from app_longevity_saas.backend.models.prediction_model import AppLongevityPredictorService

# Singleton instance of the prediction model
prediction_model = AppLongevityPredictorService()

def get_user_predictions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Prediction]:
    """Get predictions for a user"""
    return db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()

def get_prediction_by_id(db: Session, prediction_id: int, user_id: int = None) -> Prediction:
    """Get a prediction by ID"""
    query = db.query(Prediction).filter(Prediction.id == prediction_id)
    
    if user_id:
        query = query.filter(Prediction.user_id == user_id)
        
    return query.first()

def get_prediction_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get prediction statistics for a user"""
    total_predictions = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == user_id
    ).scalar()
    
    # Get predictions in the last 30 days
    last_30_days = datetime.utcnow() - timedelta(days=30)
    recent_predictions = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == user_id,
        Prediction.created_at >= last_30_days
    ).scalar()
    
    # Get average longevity score
    avg_score = db.query(func.avg(Prediction.predicted_longevity)).filter(
        Prediction.user_id == user_id
    ).scalar()
    
    # Get platform distribution
    ios_count = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == user_id,
        Prediction.app_platform == "iOS"
    ).scalar()
    
    android_count = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == user_id,
        Prediction.app_platform == "Android"
    ).scalar()
    
    return {
        "total_predictions": total_predictions,
        "recent_predictions": recent_predictions,
        "average_score": avg_score,
        "platform_distribution": {
            "ios": ios_count,
            "android": android_count
        }
    }

def delete_prediction(db: Session, prediction_id: int, user_id: int) -> bool:
    """Delete a prediction"""
    prediction = get_prediction_by_id(db, prediction_id, user_id)
    
    if not prediction:
        return False
    
    db.delete(prediction)
    db.commit()
    
    return True

def save_prediction(db: Session, user_id: int, prediction_data: Dict[str, Any]) -> Prediction:
    """Save a prediction to the database"""
    prediction = Prediction(
        user_id=user_id,
        app_name=prediction_data["app_name"],
        app_platform=prediction_data["platform"],
        app_store_id=prediction_data.get("store_id"),
        predicted_longevity=prediction_data["predicted_longevity"],
        prediction_data=json.dumps(prediction_data)
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return prediction 
