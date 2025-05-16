from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app_longevity_saas.backend.core.database import get_db
from app_longevity_saas.backend.models.user import User, Prediction
from app_longevity_saas.backend.services.auth_service import get_current_user
from app_longevity_saas.backend.models.prediction_model import AppLongevityPredictorService
from app_longevity_saas.backend.services.model_manager import model_manager
from app_longevity_saas.backend.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class PredictionCreate(BaseModel):
    app_name: str
    compare_competitors: bool = False
    model_name: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    app_name: str
    app_platform: str
    predicted_longevity: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class PredictionDetail(PredictionResponse):
    prediction_data: Dict[str, Any]
    
    class Config:
        orm_mode = True

class PredictionResult(BaseModel):
    prediction: Dict[str, Any]
    saved_id: Optional[int] = None

class ModelInfo(BaseModel):
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}

@router.post("/predict", response_model=PredictionResult)
async def predict_app_longevity(
    prediction_data: PredictionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user has reached their daily limit
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    predictions_today = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= today_start,
        Prediction.created_at <= today_end
    ).scalar()
    
    if predictions_today >= settings.FREE_PREDICTIONS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've reached your daily limit of {settings.FREE_PREDICTIONS_PER_DAY} predictions"
        )
    
    # Create a prediction service instance with the specified model (or default)
    prediction_service = AppLongevityPredictorService(model_name=prediction_data.model_name)
    
    # Make prediction
    prediction_result = await prediction_service.predict_app_longevity(
        app_name=prediction_data.app_name,
        compare_competitors=prediction_data.compare_competitors
    )
    
    # Check for errors
    if "error" in prediction_result:
        return {"prediction": prediction_result, "saved_id": None}
    
    # Save prediction to database in background
    background_tasks.add_task(
        save_prediction_to_db,
        db=db,
        user_id=current_user.id,
        prediction_result=prediction_result
    )
    
    # Calculate tentative ID (this isn't perfect but gives some indication)
    last_prediction = db.query(Prediction).order_by(Prediction.id.desc()).first()
    tentative_id = (last_prediction.id + 1) if last_prediction else 1
    
    return {"prediction": prediction_result, "saved_id": tentative_id}

@router.get("/predictions", response_model=List[PredictionResponse])
async def get_user_predictions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    
    return predictions

@router.get("/predictions/{prediction_id}", response_model=PredictionDetail)
async def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    # Parse the JSON data
    if prediction.prediction_data:
        prediction.prediction_data = json.loads(prediction.prediction_data)
    else:
        prediction.prediction_data = {}
    
    return prediction

@router.delete("/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    db.delete(prediction)
    db.commit()
    
    return None

def save_prediction_to_db(
    db: Session,
    user_id: int,
    prediction_result: Dict[str, Any]
):
    """Save prediction result to database"""
    prediction = Prediction(
        user_id=user_id,
        app_name=prediction_result["app_name"],
        app_platform=prediction_result["platform"],
        app_store_id=prediction_result.get("store_id"),
        predicted_longevity=prediction_result["predicted_longevity"],
        prediction_data=json.dumps(prediction_result)
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return prediction
