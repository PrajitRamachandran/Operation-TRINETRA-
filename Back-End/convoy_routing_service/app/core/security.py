from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Use lowercase attributes
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes) # <-- CHANGED
    to_encode.update({"exp": expire})
    # Use lowercase attributes
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm) # <-- CHANGED (x2)
    return encoded_jwt

def decode_token(token: str) -> dict | None:
    try:
        # Use lowercase attributes
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm]) # <-- CHANGED (x2)
        return payload
    except JWTError:
        return None