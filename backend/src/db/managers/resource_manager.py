from src.db.managers.base_manager import BaseManager
from src.models.orm.resource_orm import ResourceORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ResourceManager(BaseManager[ResourceORM]):
    def __init__(self):
        super().__init__(ResourceORM)

    async def get_bg(self, session: AsyncSession) -> str:
        result = await session.execute(select(self.model).limit(1))
        resource = result.scalar_one_or_none()
        return resource.bg_path if resource else ""

    async def set_bg(self, session: AsyncSession, bg_path: str) -> None:
        result = await session.execute(select(self.model).limit(1))
        resource = result.scalar_one_or_none()

        if resource:
            resource.bg_path = bg_path
        else:
            session.add(self.model(bg_path=bg_path))

        await session.flush()

def get_resource_manager() -> ResourceManager:
    return ResourceManager()