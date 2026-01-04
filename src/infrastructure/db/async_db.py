"""
# db url
# engine
# local async db session factory for DI. (session maker?)
# async db session getter function
# db declarative base
# create tables (do this in main.py)
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_session
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base
Base = declarative_base()

load_dotenv()
ASYNC_DB_URL = f"mysql+aiomysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST_NAME')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(ASYNC_DB_URL, echo=False)  # async db connection pool manager

AsyncSessionLocal = async_sessionmaker(autocommit=False,  # async session
                                       autoflush=False,
                                       bind=engine)


async def get_db_session() -> async_session:
    async with AsyncSessionLocal() as local_session:
        yield local_session


@asynccontextmanager
async def get_db_session_manual() -> async_session:
    async with AsyncSessionLocal() as local_session:
        yield local_session


async def init_db():
    try:
        async with engine.connect() as connection:
            print("Connected to database.")

    except Exception as e:
        raise Exception(f"Could not connect to db:{e}")







