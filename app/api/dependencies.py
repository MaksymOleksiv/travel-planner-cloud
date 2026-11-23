from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.project_place_repository import ProjectPlaceRepository
from app.repositories.project_repository import ProjectRepository
from app.services.artic_service import ArticService


async def get_project_repo(session: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(session)


async def get_place_repo(session: AsyncSession = Depends(get_db)) -> ProjectPlaceRepository:
    return ProjectPlaceRepository(session)


def get_artic_service() -> ArticService:
    return ArticService()
