from abc import ABC
from typing import TypeVar, Generic, Optional, List, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseManager(Generic[T], ABC):
    def __init__(self, model: Any):
        self.model: Any = model

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[T]:
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by_field(self, session: AsyncSession, value: Any, field: str) -> Optional[T]:
        result = await session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> List[T]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, **kwargs) -> T:
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        return instance

    async def update(self, session: AsyncSession, id: int, **kwargs) -> None:
        await session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )

    async def delete(self, session: AsyncSession, id: int) -> None:
        await session.execute(
            delete(self.model).where(self.model.id == id)
        )

    async def exists(self, session: AsyncSession, **filters) -> bool:
        query = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        result = await session.execute(query)
        return result.scalar() > 0

    async def count(self, session: AsyncSession, **filters) -> int:
        query = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        result = await session.execute(query)
        return result.scalar() or 0