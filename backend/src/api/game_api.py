from fastapi import APIRouter, Query
from src.services.game_service import get_game_service
from src.models.shemas.game_dto import ResumeGameRequest, StartGameDTO, GameDTO, GameResultDTO
from typing import Union

game_router = APIRouter(tags=["game"])

@game_router.get("/api/start_game", response_model=StartGameDTO)
async def start_game(question_uuid: str = Query("")):
    service = get_game_service()
    return await service.start_game(question_uuid=question_uuid)

@game_router.post("/api/resume_or_end_game", response_model=Union[GameDTO, GameResultDTO])
async def resume_or_end_game(request: ResumeGameRequest):
    service = get_game_service()
    return await service.apply_answer(
        current_metrics=[m.dict() for m in request.actual_metrics],
        question_dto=request.question,
        answer_id=request.answer_id
    )