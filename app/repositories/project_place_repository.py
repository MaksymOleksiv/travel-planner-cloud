from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_place import ProjectPlace


class ProjectPlaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_by_project(self, project_id: int) -> list[ProjectPlace]:
        result = await self.session.execute(
            select(ProjectPlace).where(ProjectPlace.project_id == project_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int, place_id: int) -> ProjectPlace | None:
        result = await self.session.execute(
            select(ProjectPlace).where(
                ProjectPlace.id == place_id,
                ProjectPlace.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_by_project(self, project_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectPlace)
            .where(ProjectPlace.project_id == project_id)
        )
        return result.scalar_one()

    async def exists_by_external_id(self, project_id: int, external_id: int) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(ProjectPlace)
            .where(
                ProjectPlace.project_id == project_id,
                ProjectPlace.external_id == external_id,
            )
        )
        return result.scalar_one() > 0

    async def create(
        self,
        project_id: int,
        external_id: int,
        title: str,
        artist_display: str | None,
        image_url: str | None,
    ) -> ProjectPlace:
        place = ProjectPlace(
            project_id=project_id,
            external_id=external_id,
            title=title,
            artist_display=artist_display,
            image_url=image_url,
        )
        self.session.add(place)
        await self.session.flush()
        await self.session.refresh(place)
        return place

    async def update(
        self,
        place: ProjectPlace,
        notes: str | None = None,
        is_visited: bool | None = None,
    ) -> ProjectPlace:
        if notes is not None:
            place.notes = notes
        if is_visited is not None:
            place.is_visited = is_visited

        await self.session.flush()
        await self.session.refresh(place)
        return place
