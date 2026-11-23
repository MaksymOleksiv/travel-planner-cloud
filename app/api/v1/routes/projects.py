from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_artic_service, get_place_repo, get_project_repo
from app.core.database import get_db
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.project import Project
from app.repositories.project_place_repository import ProjectPlaceRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.artic_service import ArticService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> list[Project]:
    projects = await project_repo.get_all(limit=limit, offset=offset)
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> Project:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError(f"Project with id={project_id} not found")
    return project


@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    project_repo: ProjectRepository = Depends(get_project_repo),
    place_repo: ProjectPlaceRepository = Depends(get_place_repo),
    artic_service: ArticService = Depends(get_artic_service),
) -> Project:
    if len(body.place_external_ids) > 10:
        raise BadRequestError("Cannot add more than 10 places to a project")

    project = await project_repo.create(
        name=body.name,
        description=body.description,
        start_date=body.start_date,
    )

    for external_id in body.place_external_ids:
        artwork = await artic_service.get_artwork(external_id)
        await place_repo.create(
            project_id=project.id,
            external_id=artwork["id"],
            title=artwork["title"],
            artist_display=artwork["artist_display"],
            image_url=artwork["image_url"],
        )

    await session.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> Project:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError(f"Project with id={project_id} not found")

    update_data = body.model_dump(exclude_unset=True)
    project = await project_repo.update(project, **update_data)

    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    project_repo: ProjectRepository = Depends(get_project_repo),
):
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise NotFoundError(f"Project with id={project_id} not found")

    if any(place.is_visited for place in project.places):
        raise BadRequestError("Cannot delete project with visited places")

    await project_repo.delete(project)
