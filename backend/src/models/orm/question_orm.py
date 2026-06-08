from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Boolean
from typing import List
import uuid
from src.core.database import Base

class QuestionORM(Base):
    __tablename__ = "game_cards"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_uuid = mapped_column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    question_text = mapped_column(Text, nullable=False)
    image_path = mapped_column(String(500), default="")
    next_question_uuid = mapped_column(String(36), nullable=True)
    is_first: Mapped[bool] = mapped_column(Boolean, default=False)

    answers: Mapped[List["AnswerORM"]] = relationship(
        "AnswerORM",
        primaryjoin="QuestionORM.question_uuid == AnswerORM.question_uuid",
        foreign_keys="AnswerORM.question_uuid",
        viewonly=False
    )