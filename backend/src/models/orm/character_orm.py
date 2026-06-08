from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime
from datetime import datetime

class CharacterORM(Base):
    __tablename__ = "game_characters"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(100), unique=True, nullable=False)
    stats = mapped_column(JSON, default=list)
    image_path = mapped_column(String(500), default="")
    created_at = mapped_column(DateTime, default=datetime.utcnow)