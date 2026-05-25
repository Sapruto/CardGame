from pydantic import BaseModel
from typing import List, Dict, Any

class MetricInfo(BaseModel):
    name: str
    description: str


class QuestionAnswer(BaseModel):
    text: str
    stats_change: Dict[str, int]

class QuestionData(BaseModel):
    uuid: str
    text: str
    answers: List[QuestionAnswer]

class GameResultRequest(BaseModel):
    final_stats: Dict[str, int]
    character_id: int


class GameStartResponse(BaseModel):
    character: Dict[str, Any]
    questions: List[QuestionData]
    metrics: List[MetricInfo]

class GameResultResponse(BaseModel):
    success: bool
    message: str
    matched_character: Dict[str, Any]
    your_stats: Dict[str, int]


class GameAssetsRequest(BaseModel):
    character: str
    questions: List[str]

class GameAssetsResponse(BaseModel):
    bg: str
    character_image: str

    questions_images: Dict[str, str]