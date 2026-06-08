from src.db.managers.base_manager import BaseManager
from src.models.orm.epilogue_orm import EpilogueORM

class EpilogueManager(BaseManager[EpilogueORM]):
    def __init__(self):
        super().__init__(EpilogueORM)

def get_epilogue_manager() -> EpilogueManager:
    return EpilogueManager()