from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int = 20, offset: int = 0) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, description: str | None, start_date) -> Project:
        project = Project(name=name, description=description, start_date=start_date)
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            if value is not None or key in kwargs:
                setattr(project, key, value)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.flush()

    async def check_and_update_status(self, project: Project) -> Project:
        await self.session.refresh(project, ["places"])

        if project.places and all(place.is_visited for place in project.places):
            project.status = ProjectStatus.completed
            await self.session.flush()
            await self.session.refresh(project)

        return project
