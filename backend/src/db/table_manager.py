from src.core.database import engine, Base
from src.models.orm.metric_orm import MetricORM
from src.models.orm.character_orm import CharacterORM
from src.models.orm.question_orm import QuestionORM
from src.models.orm.answer_orm import AnswerORM
from src.models.orm.epilogue_orm import EpilogueORM
from src.models.orm.resource_orm import ResourceORM
import logging

logger = logging.getLogger(__name__)

class InitTables:
    async def initialize_tables(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created")