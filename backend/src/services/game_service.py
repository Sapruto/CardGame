from typing import List, Union, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.managers.character_manager import get_character_manager
from src.db.managers.question_manager import get_question_manager
from src.db.managers.epilogue_manager import get_epilogue_manager
from src.db.managers.resource_manager import get_resource_manager
from src.core.database import AsyncSessionLocal
from src.models.shemas.game_dto import StartGameDTO, GameDTO, GameResultDTO, AnswerDTO, CharacterDTO, QuestionDTO, MetricDTO
from src.models.orm.question_orm import QuestionORM
from src.models.orm.answer_orm import AnswerORM
from src.models.orm.epilogue_orm import EpilogueORM
import json
import logging

logger = logging.getLogger(__name__)

class GameService:
    def __init__(self):
        self.character_manager = get_character_manager()
        self.question_manager = get_question_manager()
        self.epilogue_manager = get_epilogue_manager()
        self.resource_manager = get_resource_manager()

    async def start_game(self, question_uuid: str = "") -> StartGameDTO:
        async with AsyncSessionLocal() as session:
            if not question_uuid:
                result = await session.execute(
                    select(QuestionORM)
                    .where(QuestionORM.is_first == True)
                    .options(selectinload(QuestionORM.answers))
                    .limit(1)
                )
                question = result.scalar_one_or_none()
                if not question:
                    result = await session.execute(
                        select(QuestionORM)
                        .order_by(QuestionORM.id)
                        .options(selectinload(QuestionORM.answers))
                        .limit(1)
                    )
                    question = result.scalar_one_or_none()
            else:
                result = await session.execute(
                    select(QuestionORM)
                    .where(QuestionORM.question_uuid == question_uuid)
                    .options(selectinload(QuestionORM.answers))
                )
                question = result.scalar_one_or_none()

            if not question:
                raise ValueError("Question not found")

            character = await self.character_manager.get_random(session)
            bg_path = await self.resource_manager.get_bg(session)

            answer_dtos = []
            for a in question.answers:
                stats_change = a.stats_change if isinstance(a.stats_change, list) else json.loads(
                    a.stats_change) if a.stats_change else []
                answer_dtos.append(AnswerDTO(
                    id=a.id,
                    text=a.answer_text,
                    stats_change=stats_change,
                    order_index=a.order_index
                ))

            char_stats = character.stats if isinstance(character.stats, list) else json.loads(
                character.stats) if character.stats else []

            character_dto = CharacterDTO(
                id=character.id,
                name=character.name,
                stats=char_stats,
                image_path=character.image_path or ""
            )

            question_dto = QuestionDTO(
                id=question.id,
                uuid=question.question_uuid,
                text=question.question_text,
                image_path=question.image_path or "",
                next_question_uuid=question.next_question_uuid,
                answers=answer_dtos
            )

            return StartGameDTO(
                character=character_dto,
                question=question_dto,
                bg_path=bg_path
            )

    async def apply_answer(self, current_metrics: List[Dict[str, Any]], question_dto: QuestionDTO, answer_id: int) -> Union[GameDTO, GameResultDTO]:
        async with AsyncSessionLocal() as session:
            selected_answer_dto = None
            for answer in question_dto.answers:
                if answer.id == answer_id:
                    selected_answer_dto = answer
                    break

            if not selected_answer_dto:
                raise ValueError(f"Answer {answer_id} not found")

            new_metrics = self._apply_stats_changes(current_metrics, selected_answer_dto.stats_change)

            if question_dto.next_question_uuid:
                result = await session.execute(
                    select(QuestionORM)
                    .where(QuestionORM.question_uuid == question_dto.next_question_uuid)
                    .options(selectinload(QuestionORM.answers))
                )
                next_question_orm = result.scalar_one_or_none()

                if not next_question_orm:
                    raise ValueError("Next question not found")

                next_answer_dtos = []
                for a in next_question_orm.answers:
                    stats_change = a.stats_change if isinstance(a.stats_change, list) else json.loads(
                        a.stats_change) if a.stats_change else []
                    next_answer_dtos.append(AnswerDTO(
                        id=a.id,
                        text=a.answer_text,
                        stats_change=stats_change,
                        order_index=a.order_index
                    ))

                next_question_dto = QuestionDTO(
                    id=next_question_orm.id,
                    uuid=next_question_orm.question_uuid,
                    text=next_question_orm.question_text,
                    image_path=next_question_orm.image_path or "",
                    next_question_uuid=next_question_orm.next_question_uuid,
                    answers=next_answer_dtos
                )

                new_metrics_dto = []
                for m in new_metrics:
                    new_metrics_dto.append(MetricDTO(
                        id=m.get("id", 0),
                        metric_name=m.get("metric_name", ""),
                        description=m.get("description", ""),
                        default_value=m.get("default_value", 0)
                    ))

                return GameDTO(actual_metrics=new_metrics_dto, question=next_question_dto)

            epilogues = await self.epilogue_manager.get_all(session)
            epilogue = self._find_epilogue(new_metrics, epilogues)

            return GameResultDTO(epilogue=epilogue)

    def _apply_stats_changes(self, current_metrics: List[Dict[str, Any]], stats_changes: List[Dict[str, Any]]) -> List[
        Dict[str, Any]]:
        metrics_dict = {m["metric_name"]: m for m in current_metrics}
        for change in stats_changes:
            if change["stat_name"] in metrics_dict:
                delta = change["delta"]
                old = metrics_dict[change["stat_name"]]
                old["default_value"] = old.get("default_value", 0) + delta
        return list(metrics_dict.values())

    def _find_epilogue(self, metrics: List[Dict[str, Any]], epilogues: List[EpilogueORM]) -> Dict[str, Any]:
        if not epilogues:
            return None
        ep = epilogues[0]
        return {
            "id": ep.id,
            "text": ep.text,
            "stats": ep.stats if isinstance(ep.stats, dict) else json.loads(ep.stats)
        }

def get_game_service() -> GameService:
    return GameService()