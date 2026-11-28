from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.project_place_repository import ProjectPlaceRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.services.artic_service import ArticService

# Reads "Authorization: Bearer <token>"; tokenUrl powers the "Authorize" button in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_project_repo(session: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(session)


async def get_place_repo(session: AsyncSession = Depends(get_db)) -> ProjectPlaceRepository:
    return ProjectPlaceRepository(session)


async def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_artic_service() -> ArticService:
    return ArticService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),  # no header -> 401 automatically
    users: UserRepository = Depends(get_user_repo),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized
    user = await users.get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user
