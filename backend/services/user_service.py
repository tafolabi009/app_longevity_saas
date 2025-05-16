from sqlalchemy.orm import Session

from app_longevity_saas.backend.models.user import User
from app_longevity_saas.backend.core.security import get_password_hash
from app_longevity_saas.backend.api.auth import UserCreate

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users"""
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_data: dict) -> User:
    """Update a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None
    
    # Update user fields
    for key, value in user_data.items():
        if key == "password":
            # Hash the password if it's being updated
            setattr(db_user, "hashed_password", get_password_hash(value))
        elif hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int) -> User:
    """Deactivate a user (soft delete)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user 
