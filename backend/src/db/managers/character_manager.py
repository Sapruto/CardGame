from typing import Optional
from src.db.managers.base_manager import BaseManager
from src.models.orm.character_orm import CharacterORM
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

class CharacterManager(BaseManager[CharacterORM]):
    def __init__(self):
        super().__init__(CharacterORM)

    async def get_random(self, session: AsyncSession) -> Optional[CharacterORM]:
        result = await session.execute(
            select(self.model).order_by(func.random()).limit(1)
        )
        return result.scalar_one_or_none()

def get_character_manager() -> CharacterManager:
    return CharacterManager()