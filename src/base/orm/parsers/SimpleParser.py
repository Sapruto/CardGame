from abc import ABC, abstractmethod
from typing import Dict
from src.base.orm.InternalBD import OperatorsInternal

class ParserTemplete(ABC):
    def __init__(self, operators: OperatorsInternal):
        self.operators = operators
        self.replace_map = self._build_replace_map()
    
    @abstractmethod
    def _build_replace_map(self) -> Dict[str, str]:
        pass
    
    def parse(self, sql_template: str) -> str:
        result = sql_template

        self.replace_map = {k: v for k, v in self.replace_map.items() 
                if isinstance(k, str)}
        
        for from_op, to_op in self.replace_map.items():
            result = result.replace(from_op, to_op)
        
        result = self._post_process(result)
        
        return result
    
    def _post_process(self, sql: str) -> str:
        return sql