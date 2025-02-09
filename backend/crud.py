from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import selectinload 
from sqlalchemy.exc import IntegrityError
from backend.models import User, Scan
from backend.schemas import UserCreate, UserUpdate, ScanCreate
from backend.auth import hash_password, verify_password
from datetime import datetime
from passlib.context import CryptContext
from typing import List, Optional
from fastapi import HTTPException

async def get_users(db: AsyncSession):
    result = await db.execute(
        select(User).options(selectinload(User.scans))  
    )
    return result.scalars().all()

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User)
        .filter(User.id == user_id)
        .options(selectinload(User.scans))
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)

    
    result = await db.execute(select(func.count()).where(User.id >= 101))
    manual_user_count = result.scalar_one_or_none() or 0

    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        badge_code=user.badge_code,
        hashed_password=hashed_password,
        updated_at=datetime.utcnow(),
        is_admin=True if manual_user_count == 0 else False 
    )

    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)

        user_with_scans = await db.execute(
            select(User).options(selectinload(User.scans)).filter(User.id == db_user.id)
        )
        return user_with_scans.scalars().first()
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User with this email or badge code already exists")
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()

    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()

    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user


async def create_scan(db: AsyncSession, user_id: int, scan: ScanCreate):
    db_scan = Scan(
        user_id=user_id,
        activity_name=scan.activity_name,
        activity_category=scan.activity_category,
        scanned_at=datetime.utcnow()
    )
    db.add(db_scan)
    await db.commit()
    await db.refresh(db_scan)
    return db_scan


async def get_scans(db: AsyncSession, min_frequency: int = 0, activity_category: Optional[str] = None):
    query = select(Scan)

    if activity_category:
        query = query.filter(Scan.activity_category == activity_category)

    result = await db.execute(query)
    return result.scalars().all()  

async def get_user_scans(db: AsyncSession, user_id: int):
    result = await db.execute(select(Scan).filter(Scan.user_id == user_id))
    return result.scalars().all()
