from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text

class MetricORM(Base):
    __tablename__ = "metrics_definition"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_name = mapped_column(String(100), unique=True, nullable=False)
    description = mapped_column(Text, default="")
    default_value = mapped_column(Integer, default=0)