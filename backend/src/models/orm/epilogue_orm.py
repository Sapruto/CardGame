from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, JSON

class EpilogueORM(Base):
    __tablename__ = "epilogs"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    text = mapped_column(Text, nullable=False)
    stats = mapped_column(JSON, default=dict)