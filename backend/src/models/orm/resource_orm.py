from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class ResourceORM(Base):
    __tablename__ = "resources"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    bg_path = mapped_column(String(500), default="")