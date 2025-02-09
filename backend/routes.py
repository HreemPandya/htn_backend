from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend import crud, schemas, database
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.sql import func
from datetime import datetime
from backend.schemas import Token, UserAuth
from backend.models import Scan, User, Connection
from backend.auth import create_access_token, decode_access_token
from backend.crud import authenticate_user
from backend.database import AsyncSessionMaker
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status
from sqlalchemy import delete

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_db():
    async with AsyncSessionMaker() as session:
        yield session


@router.get("/users", response_model=List[schemas.User], summary="List All Registered Users")
async def read_users(db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db)

@router.get("/users/{user_id}", response_model=schemas.User,  summary="Retrieve User Details")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.User, summary="Register a New User")
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user)

async def get_current_admin(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):

    email = decode_access_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(get_current_admin) 
):
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(delete(Scan).where(Scan.user_id == user_id))
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    return {"message": f"User {user.email} deleted successfully"}


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user_update: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/scans/{user_id}", response_model=schemas.Scan)
async def add_scan(user_id: int, scan: schemas.ScanCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_scan(db, user_id, scan)


@router.get("/scans", response_model=List[schemas.Scan])
async def read_scans(min_frequency: int = 0, activity_category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await crud.get_scans(db, min_frequency, activity_category)

@router.get("/users/{user_id}/scans", response_model=List[schemas.Scan])
async def read_user_scans(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_user_scans(db, user_id)

@router.get("/scan-stats")
async def scan_stats(
    min_frequency: int = 0,
    max_frequency: Optional[int] = None,
    activity_name: Optional[str] = None,
    activity_category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(
        Scan.activity_name,
        Scan.activity_category,
        func.count(Scan.id).label("frequency")
    ).group_by(Scan.activity_name, Scan.activity_category)

    if min_frequency > 0:
        query = query.having(func.count(Scan.id) >= min_frequency)

    if max_frequency is not None:
        query = query.having(func.count(Scan.id) <= max_frequency)

    if activity_name:
        query = query.filter(Scan.activity_name == activity_name)

    if activity_category:
        query = query.filter(Scan.activity_category == activity_category)

    result = await db.execute(query)
    raw_data = result.fetchall()


    scan_data = [
        {"activity_name": row[0], "activity_category": row[1], "frequency": row[2]} 
        for row in raw_data
    ]

    return scan_data 


@router.get("/scan-timeline")
async def scan_timeline(activity_name: str, db: AsyncSession = Depends(get_db)):
    query = select(
        func.date_trunc('hour', Scan.scanned_at).label("time_slot"),
        func.count(Scan.id).label("scan_count")
    ).where(Scan.activity_name == activity_name).group_by("time_slot")

    result = await db.execute(query)
    raw_data = result.fetchall()

    
    timeline_data = [
        {"time_slot": row[0].isoformat(), "scan_count": row[1]} for row in raw_data
    ]

    if not timeline_data:
        raise HTTPException(status_code=404, detail="No scan data found for this activity.")

    return timeline_data


@router.post("/check-in")
async def check_in(badge_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.badge_code == badge_code))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.updated_at:
        raise HTTPException(status_code=400, detail="User already checked in")
    user.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "User checked in successfully"}


@router.post("/check-out")
async def check_out(badge_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.badge_code == badge_code))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.updated_at = None  
    await db.commit()
    return {"message": "User checked out successfully"}


@router.post("/connect/{user_id1}/{user_id2}")
async def connect_users(user_id1: int, user_id2: int, db: AsyncSession = Depends(get_db)):
    if user_id1 == user_id2:
        raise HTTPException(status_code=400, detail="Cannot connect a user to themselves")
    new_connection = Connection(user_id1=user_id1, user_id2=user_id2)
    db.add(new_connection)
    await db.commit()
    return {"message": "Users connected successfully"}


@router.post("/snacks/{user_id}")
async def claim_snack(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Scan).filter(Scan.user_id == user_id, Scan.activity_name == "Midnight Snack"))
    existing_snack = result.scalars().first()
    if existing_snack:
        raise HTTPException(status_code=403, detail="You have already claimed your midnight snack")
    new_snack_scan = Scan(user_id=user_id, activity_name="Midnight Snack", activity_category="Food", scanned_at=datetime.utcnow())
    db.add(new_snack_scan)
    await db.commit()
    return {"message": "Midnight snack claimed!"}

@router.get("/leaderboard")
async def leaderboard(db: AsyncSession = Depends(get_db)):
    query = select(User.id, User.name, func.count(Scan.id).label("scan_count")).join(Scan).group_by(User.id).order_by(func.count(Scan.id).desc()).limit(10)
    result = await db.execute(query)
    raw_data = result.fetchall()

    return [{"user_id": row[0], "name": row[1], "scans": row[2]} for row in raw_data]

@router.get("/popular-activities")
async def popular_activities(db: AsyncSession = Depends(get_db)):
    query = select(Scan.activity_name, func.count(Scan.id).label("scan_count")).group_by(Scan.activity_name).order_by(func.count(Scan.id).desc())
    result = await db.execute(query)
    raw_data = result.fetchall()

    return [{"activity_name": row[0], "scans": row[1]} for row in raw_data]

@router.get("/peak-times")
async def peak_times(db: AsyncSession = Depends(get_db)):
    query = select(func.date_trunc('hour', Scan.scanned_at).label("time_slot"), func.count(Scan.id).label("scan_count")).group_by("time_slot").order_by("time_slot")
    result = await db.execute(query)
    raw_data = result.fetchall()

    return {row[0].strftime("%I %p - %I %p"): row[1] for row in raw_data}

@router.get("/users/{user_id}/activity-log")
async def activity_log(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Scan.activity_name, Scan.scanned_at).filter(Scan.user_id == user_id).order_by(Scan.scanned_at.asc())
    result = await db.execute(query)
    raw_data = result.fetchall()

    return [{"activity": row[0], "time": row[1].strftime("%I:%M %p")} for row in raw_data]

import random

@router.get("/random-winner")
async def random_winner(db: AsyncSession = Depends(get_db)):
    query = select(User.id, User.name, User.badge_code).join(Scan).group_by(User.id).having(func.count(Scan.id) >= 3)
    result = await db.execute(query)
    eligible_users = result.fetchall()

    if not eligible_users:
        raise HTTPException(status_code=404, detail="No eligible users found")

    winner = random.choice(eligible_users)

    return {"winner": winner[1], "badge_code": winner[2]}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

@router.get("/protected")
async def protected_route(user: UserAuth = Depends(get_current_user)):
    return {"message": f"Hello {user.email}, you accessed a protected route!"}

@router.put("/promote-admin/{user_id}")
async def promote_admin(user_id: int, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
   
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="User is already an admin")

    user.is_admin = True  
    await db.commit()
    return {"message": f"User {user.name} has been promoted to admin."}

