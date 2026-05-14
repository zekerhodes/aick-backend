from fastapi import FastAPI, APIRouter, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from db import client
from auth import UserIn, UserLogin, TokenResponse, signup_user, login_user, get_current_user
from routes_assets import router as assets_router
from routes_master import router as master_router
from routes_reports import router as reports_router
from seed import seed_if_empty

app = FastAPI(title='AIC Kapsowar Hospital Asset Management API')

api = APIRouter(prefix='/api')


@api.get('/')
async def root():
    return {
        'app': 'AIC Kapsowar Hospital Asset Management',
        'status': 'ok',
        'features': {
            'pharmacy': os.environ.get('FEATURE_PHARMACY', 'false') == 'true',
            'inventory': os.environ.get('FEATURE_INVENTORY', 'false') == 'true',
        },
    }


@api.post('/auth/signup', response_model=TokenResponse)
async def auth_signup(data: UserIn):
    return await signup_user(data)


@api.post('/auth/login', response_model=TokenResponse)
async def auth_login(data: UserLogin):
    return await login_user(data)


@api.get('/auth/me')
async def auth_me(user: dict = Depends(get_current_user)):
    user.pop('_id', None)
    user.pop('password_hash', None)
    return user


# Include routers
api.include_router(assets_router)
api.include_router(reports_router)
api.include_router(master_router)  # generic CRUD (must come last to avoid conflicting paths)

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event('startup')
async def on_startup():
    try:
        seeded = await seed_if_empty()
        if seeded:
            logger.info('AIC Kapsowar database seeded with initial data')
        else:
            logger.info('Database already initialised — skipping seed')
    except Exception as e:
        logger.exception(f'Seed failed: {e}')


@app.on_event('shutdown')
async def on_shutdown():
    client.close()
