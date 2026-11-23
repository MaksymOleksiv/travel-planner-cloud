from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_artic_service, get_place_repo, get_project_repo
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.project_place import ProjectPlace
from app.repositories.project_place_repository import ProjectPlaceRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_place import (
    ProjectPlaceCreate,
    ProjectPlaceRead,
    ProjectPlaceUpdate,
)
from app.services.artic_service import ArticService

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Project Places"])


@router.get("/", response_model=list[ProjectPlaceRead])
async def list_places(
    project_id: int,
    project_repo: ProjectRepository = Depends(get_project_repo),
    place_repo: ProjectPlaceRepository = Depends(get_place_repo),
) -> list[ProjectPlace]:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    places = await place_repo.get_all_by_project(project_id)
    return places


@router.get("/{place_id}", response_model=ProjectPlaceRead)
async def get_place(
    project_id: int,
    place_id: int,
    project_repo: ProjectRepository = Depends(get_project_repo),
    place_repo: ProjectPlaceRepository = Depends(get_place_repo),
) -> ProjectPlace:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    place = await place_repo.get_by_id(project_id, place_id)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found in this project",
        )

    return place


@router.post("/", response_model=ProjectPlaceRead, status_code=201)
async def add_place(
    project_id: int,
    body: ProjectPlaceCreate,
    project_repo: ProjectRepository = Depends(get_project_repo),
    place_repo: ProjectPlaceRepository = Depends(get_place_repo),
    artic_service: ArticService = Depends(get_artic_service),
) -> ProjectPlace:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    current_count = await place_repo.count_by_project(project_id)
    if current_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add more than 10 places to a project",
        )

    if await place_repo.exists_by_external_id(project_id, body.external_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Place with external_id {body.external_id} already exists in this project",
        )

    try:
        artwork_data = await artic_service.get_artwork(body.external_id)
    except (NotFoundError, BadRequestError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    place = await place_repo.create(
        project_id=project_id,
        external_id=artwork_data["id"],
        title=artwork_data["title"],
        artist_display=artwork_data["artist_display"],
        image_url=artwork_data["image_url"],
    )

    return place


@router.patch("/{place_id}", response_model=ProjectPlaceRead)
async def update_place(
    project_id: int,
    place_id: int,
    body: ProjectPlaceUpdate,
    project_repo: ProjectRepository = Depends(get_project_repo),
    place_repo: ProjectPlaceRepository = Depends(get_place_repo),
) -> ProjectPlace:
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    place = await place_repo.get_by_id(project_id, place_id)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found in this project",
        )

    update_data = body.model_dump(exclude_unset=True)
    place = await place_repo.update(
        place,
        notes=update_data.get("notes"),
        is_visited=update_data.get("is_visited"),
    )

    await project_repo.check_and_update_status(project)

    return place
