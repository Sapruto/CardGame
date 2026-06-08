from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from src.core.database import Base

class AnswerORM(Base):
    __tablename__ = "game_answers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_uuid: Mapped[str] = mapped_column(String(36), ForeignKey("game_cards.question_uuid", ondelete="CASCADE"))
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    stats_change: Mapped[dict] = mapped_column(JSON, default=list)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    question: Mapped["QuestionORM"] = relationship(
        "QuestionORM",
        back_populates="answers",
        foreign_keys=[question_uuid]
    )