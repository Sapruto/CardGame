from src.db.managers.base_manager import BaseManager
from src.models.orm.metric_orm import MetricORM

class MetricManager(BaseManager[MetricORM]):
    def __init__(self):
        super().__init__(MetricORM)

def get_metric_manager():
    return MetricManager()