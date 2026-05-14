from datetime import datetime, timedelta
from typing import Optional
import os
import uuid
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field

from db import coll

JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me-in-production-aic-kapsowar')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRES_HOURS = 24 * 7  # 1 week

pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
bearer = HTTPBearer(auto_error=False)


class UserIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = 'Asset Manager'


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    user: UserOut
    token: str
    token_type: str = 'bearer'


def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(pw, hashed)
    except Exception:
        return False


def create_token(user_id: str, email: str) -> str:
    payload = {
        'sub': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail='Missing auth token')
    payload = decode_token(creds.credentials)
    user = await coll('users').find_one({'id': payload['sub']})
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


async def signup_user(data: UserIn) -> TokenResponse:
    existing = await coll('users').find_one({'email': data.email})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    user_id = str(uuid.uuid4())
    doc = {
        'id': user_id,
        'name': data.name,
        'email': data.email,
        'role': data.role or 'Asset Manager',
        'password_hash': hash_password(data.password),
        'created_at': datetime.utcnow(),
    }
    await coll('users').insert_one(doc)
    token = create_token(user_id, data.email)
    return TokenResponse(
        user=UserOut(id=user_id, name=data.name, email=data.email, role=doc['role'], created_at=doc['created_at']),
        token=token,
    )


async def login_user(data: UserLogin) -> TokenResponse:
    user = await coll('users').find_one({'email': data.email})
    if not user or not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    token = create_token(user['id'], user['email'])
    return TokenResponse(
        user=UserOut(id=user['id'], name=user['name'], email=user['email'], role=user['role'], created_at=user['created_at']),
        token=token,
    )
