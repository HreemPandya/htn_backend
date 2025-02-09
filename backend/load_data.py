import json
import os
import asyncio
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from backend.database import AsyncSessionMaker
from backend.models import User, Scan
from datetime import datetime, timezone
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "users.json")

def generate_random_badge_code():
    words = ["alpha", "beta", "gamma", "delta", "omega", "sigma", "tau", "zeta", "phi"]
    return "-".join(random.sample(words, 4))

async def load_users():
   
    
    if not os.path.exists(JSON_FILE):
        print(f"❌ ERROR: {JSON_FILE} not found.")
        return []

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            users_data = json.load(file)

        if not users_data:
            print("⚠️ WARNING: users.json is empty.")
            return []

        async with AsyncSessionMaker() as db:
            print("🔄 Checking if database is empty...")

            
            existing_users = await db.execute(select(User))
            if existing_users.scalars().first():
                print("✅ Database already has users, skipping reload from users.json.")
                return  

            print("🔄 Loading users into database from users.json...")

            for user in users_data:
                if "email" not in user or "name" not in user or "phone" not in user:
                    print(f"⚠️ Skipping user with missing fields: {user}")
                    continue

                badge_code = user.get("badge_code", "").strip()
                if not badge_code:
                    badge_code = generate_random_badge_code()

               
                existing_badge = await db.execute(select(User).where(User.badge_code == badge_code))
                while existing_badge.scalars().first():
                    badge_code = generate_random_badge_code()
                    existing_badge = await db.execute(select(User).where(User.badge_code == badge_code))

                updated_at_naive = datetime.now(timezone.utc).replace(tzinfo=None)

                new_user = User(
                    name=user["name"],
                    email=user["email"],
                    phone=user["phone"],
                    badge_code=badge_code,
                    hashed_password=pwd_context.hash("defaultpassword"),
                    updated_at=updated_at_naive,
                    is_admin=user.get("is_admin", False)
                )
                db.add(new_user)
                await db.flush()

                for scan in user.get("scans", []):
                    new_scan = Scan(
                        user_id=new_user.id,
                        activity_name=scan["activity_name"],
                        activity_category=scan["activity_category"],
                        scanned_at=datetime.fromisoformat(scan["scanned_at"]).replace(tzinfo=None)
                    )
                    db.add(new_scan)

            await db.commit()
            print(f"✅ Users and scans successfully loaded into the database.")

    except json.JSONDecodeError:
        print("❌ ERROR: Invalid JSON format in users.json.")
    except SQLAlchemyError as e:
        print(f"❌ Database Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(load_users())  