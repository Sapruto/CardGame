from typing import Dict, Optional, List
from pydantic import BaseModel

class AnswerGetRequest(BaseModel):
    card_uuid: str

class CharacterResponse(BaseModel):
    id: int
    name: str
    stats: Dict[str, int]
    image_path: str

class CardResponse(BaseModel):
    id: int
    card_uuid: str
    card_text: str
    image_path: str

class AnswerResponse(BaseModel):
    id: int
    card_uuid: str
    answer_text: str
    stats_change: Dict[str, int]
    order_index: int

class CharacterCreateRequest(BaseModel):
    name: str
    stats: Dict[str, int]
    image_path: str

class CharacterUpdateRequest(BaseModel):
    name: Optional[str]
    stats: Optional[Dict[str, int]]
    image_path: Optional[str]

class CardCreateRequest(BaseModel):
    card_text: str
    image_path: str

class CardUpdateRequest(BaseModel):
    card_text: Optional[str]
    image_path: Optional[str]

class AnswerCreateRequest(BaseModel):
    card_uuid: str
    answer_text: str
    stats_change: Dict[str, int]
    order_index: int

class AnswerUpdateRequest(BaseModel):
    answer_text: Optional[str]
    stats_change: Optional[Dict[str, int]]
    order_index: Optional[int]

class MetricCreateRequest(BaseModel):
    metric_name: str
    description: str
    default_value: float

class MetricUpdateRequest(BaseModel):
    metric_name: Optional[str]
    description: Optional[str]
    default_value: Optional[float]

class ImageUploadRequest(BaseModel):
    folder: str

class ImageResponse(BaseModel):
    id: int
    path: str