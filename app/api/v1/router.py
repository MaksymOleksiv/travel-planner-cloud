from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.project_places import router as project_places_router
from app.api.v1.routes.projects import router as projects_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(project_places_router)
