from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core import security
from ..db import crud, models, database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None or payload.get("sub") is None:
        raise credentials_exception
    username: str = payload.get("sub")
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def role_checker(allowed_roles: list[models.UserRole]):
    def check_roles(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user
    return check_roles

# Pre-defined dependencies for convenience
is_commander = role_checker([models.UserRole.COMMANDER])
is_analyst_or_commander = role_checker([models.UserRole.ANALYST, models.UserRole.COMMANDER])
is_operator_or_commander = role_checker([models.UserRole.OPERATOR, models.UserRole.COMMANDER])