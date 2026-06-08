from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, List

class MetricCreateSchema(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    default_value: int = Field(0, ge=-1000, le=1000)

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Metric name cannot be empty")
        return v.strip()

class MetricUpdateSchema(BaseModel):
    metric_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    default_value: Optional[int] = Field(None, ge=-1000, le=1000)

class MetricResponseSchema(BaseModel):
    id: int
    metric_name: str
    description: str
    value: int


class CharacterCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    image_path: str = ""
    stats: Optional[Dict[str, int]] = None

class CharacterUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    stats: Optional[Dict[str, int]] = None
    image_path: Optional[str] = None

class CharacterResponseSchema(BaseModel):
    id: int
    name: str
    stats: Optional[List[dict]] = None
    image_path: str


class CardCreateSchema(BaseModel):
    card_text: str = Field(..., min_length=1)
    image_path: str = ""
    next_question_uuid: Optional[str] = Field(None, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    is_first: bool = False

class CardUpdateSchema(BaseModel):
    card_text: Optional[str] = Field(None, min_length=1)
    image_path: Optional[str] = None
    next_question_uuid: Optional[str] = Field(None, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    is_first: Optional[bool] = None

class CardResponseSchema(BaseModel):
    id: int
    card_uuid: str
    card_text: str
    image_path: str
    next_question_uuid: Optional[str]
    is_first: bool


class StatChangeSchema(BaseModel):
    stat_name: str = Field(..., min_length=1)
    delta: int

class AnswerCreateSchema(BaseModel):
    card_uuid: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    answer_text: str = Field(..., min_length=1)
    order_index: int = Field(0, ge=0)
    stats_change: List[StatChangeSchema] = []

class AnswerUpdateSchema(BaseModel):
    answer_text: Optional[str] = Field(None, min_length=1)
    order_index: Optional[int] = Field(None, ge=0)
    stats_change: Optional[List[StatChangeSchema]] = None

class AnswerResponseSchema(BaseModel):
    id: int
    card_uuid: str
    answer_text: str
    stats_change: List[StatChangeSchema]
    order_index: int