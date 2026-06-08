from pydantic import BaseModel
from typing import List, Optional

class CharacterDTO(BaseModel):
    id: int
    name: str
    stats: List[dict]
    image_path: str

class AnswerDTO(BaseModel):
    id: int
    text: str
    stats_change: List[dict]
    order_index: int

class QuestionDTO(BaseModel):
    id: int
    uuid: str
    text: str
    image_path: str
    next_question_uuid: Optional[str]
    answers: List[AnswerDTO]

class MetricDTO(BaseModel):
    id: int
    metric_name: str
    description: str
    default_value: int

class EpilogueDTO(BaseModel):
    id: int
    text: str
    stats: dict

class StartGameDTO(BaseModel):
    character: CharacterDTO
    question: QuestionDTO
    bg_path: str

class GameDTO(BaseModel):
    actual_metrics: List[MetricDTO]
    question: QuestionDTO

class GameResultDTO(BaseModel):
    epilogue: EpilogueDTO

class ResumeGameRequest(BaseModel):
    actual_metrics: List[MetricDTO]
    question: QuestionDTO
    answer_id: int