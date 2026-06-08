from fastapi import APIRouter, Request, Query
from src.api.requests.game_requests import GameResultRequest, GameStartResponse, GameResultResponse, GameAssetsResponse, GameAssetsRequest
from src.services.game_service import GameService

game_router = APIRouter(tags=["game"])

def get_service():
    return GameService()

@game_router.get("/api/start_game")
def start_game(max_rounds: int = Query(10)) -> GameStartResponse:
    service = get_service()
    return service.get_new_game(max_rounds=max_rounds)

@game_router.post("/api/get_assets")
def get_assets(request: GameAssetsRequest) -> GameAssetsResponse:
    service = get_service()
    return service.get_assets(request)


@game_router.post("/api/end_game")
def end_game(result: GameResultRequest) -> GameResultResponse:
    service = get_service()
    return service.process_game_result(result.final_stats, result.character_id)