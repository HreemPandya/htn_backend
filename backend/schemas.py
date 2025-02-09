from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


class ScanBase(BaseModel):
    activity_name: str
    activity_category: str


class ScanCreate(ScanBase):
    pass


class Scan(ScanBase):
    id: int
    user_id: int
    scanned_at: datetime

    class Config:
        from_attributes = True   


class UserBase(BaseModel):
    name: str
    email: EmailStr  
    phone: str
    badge_code: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    badge_code: str
    updated_at: datetime
    is_active: bool  
    is_admin: bool 

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    updated_at: datetime
    scans: List[Scan] = []

    class Config:
        from_attributes = True  

class ConnectionBase(BaseModel):
    user_id1: int
    user_id2: int

class ConnectionCreate(ConnectionBase):
    pass

class Connection(ConnectionBase):
    id: int
    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    scans: int

class PopularActivity(BaseModel):
    activity_name: str
    scans: int

class PeakTime(BaseModel):
    time_slot: str
    scan_count: int

class ActivityLogEntry(BaseModel):
    activity: str
    time: str

class RandomWinner(BaseModel):
    winner: str
    badge_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserAuth(BaseModel):
    email: str
    password: str