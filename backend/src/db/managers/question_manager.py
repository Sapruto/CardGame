from typing import Optional
from src.db.managers.base_manager import BaseManager
from src.models.orm.question_orm import QuestionORM
from src.models.orm.answer_orm import AnswerORM
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

class QuestionManager(BaseManager[QuestionORM]):
    def __init__(self):
        super().__init__(QuestionORM)

    async def get_first(self, session: AsyncSession) -> Optional[QuestionORM]:
        result = await session.execute(
            select(self.model).where(self.model.is_first == True).limit(1)
        )
        question = result.scalar_one_or_none()

        if not question:
            result = await session.execute(
                select(self.model).order_by(self.model.id).limit(1)
            )
            question = result.scalar_one_or_none()

        return question

    async def set_as_first(self, session: AsyncSession, uuid: str) -> None:
        await session.execute(
            update(self.model).values(is_first=False)
        )
        await session.execute(
            update(self.model).where(self.model.question_uuid == uuid).values(is_first=True)
        )
        await session.flush()

    async def get_with_answers(self, session: AsyncSession, uuid: str) -> Optional[QuestionORM]:
        result = await session.execute(
            select(self.model).where(self.model.question_uuid == uuid)
        )
        question = result.scalar_one_or_none()

        if question:
            answers_result = await session.execute(
                select(AnswerORM)
                .where(AnswerORM.question_uuid == question.question_uuid)
                .order_by(AnswerORM.order_index)
            )
            question.answers = answers_result.scalars().all()

        return question

def get_question_manager() -> QuestionManager:
    return QuestionManager()