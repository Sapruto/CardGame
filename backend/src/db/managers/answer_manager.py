from typing import List
from src.db.managers.base_manager import BaseManager
from src.models.orm.answer_orm import AnswerORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class AnswerManager(BaseManager[AnswerORM]):
    def __init__(self):
        super().__init__(AnswerORM)

    async def get_by_question(self, session: AsyncSession, question_uuid: str) -> List[AnswerORM]:
        result = await session.execute(
            select(self.model)
            .where(self.model.question_uuid == question_uuid)
            .order_by(self.model.order_index)
        )
        return list(result.scalars().all())

def get_answer_manager() -> AnswerManager:
    return AnswerManager()