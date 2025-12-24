from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
import logging
from dotenv import load_dotenv
from src.api.routes.health_check import router as health_check_router

# initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] %(name)s: %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('app.log')
                              ]
                    )
logger = logging.getLogger("app")

# load secretes
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up tasks
    # initialize db
    # create tables
    # load ml model initially once
    # instantiate ws connection manager
    logger.info("Application starting...")

    yield

    # clean up tasks
    logger.info("Application closing...")

app = FastAPI(lifespan=lifespan)

# register routes
app.include_router(health_check_router)

