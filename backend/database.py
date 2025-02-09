from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:5433/hackathon"


async_engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)

\
AsyncSessionMaker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()


async def get_db():
    async with AsyncSessionMaker() as session:
        yield session
