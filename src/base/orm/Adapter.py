from typing import Dict, List, Any
from src.base.orm.parsers.SimpleParser import ParserTemplete

class Adapter:
    def __init__(self, parser: ParserTemplete):
        self.parser = parser
    
    def adapt(self, sql_template: str) -> str:
        return self.parser.parse(sql_template)
    
    def adapt_select(self, table: str, columns: str = "*", 
                    where: List[Dict] = None) -> str:
        sql_template = f"{self.parser.operators.SELECT} {columns} "
        sql_template += f"{self.parser.operators.FROM} {table}"
        
        if where:
            where_parts = []
            for cond in where:
                col = cond['column']
                op = cond.get('operator', self.parser.operators.EQUALS)
                val = cond.get('value')
                
                if op.upper() in ['IS NULL', 'IS NOT NULL']:
                    where_parts.append(f"{col} {op}")
                else:
                    where_parts.append(f"{col} {op} {self.parser.operators.PLACEHOLDER}")
            
            where_str = f" {self.parser.operators.AND} ".join(where_parts)
            sql_template += f" {self.parser.operators.WHERE} {where_str}"
        
        return self.parser.parse(sql_template)