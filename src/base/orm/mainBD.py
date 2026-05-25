from typing import List, Dict, Optional, Tuple, Union
from src.base.orm.InternalBD import GeneralMethods, DataTypesInternal, OperatorsInternal
from src.base.orm.InternalBD import Identifier
from src.base.orm.Adapter import Adapter
from src.base.orm.parsers.ParserToSqlite3 import ParserToSqlite3
from src.base.orm.parsers.ParserToPostgreSQL import ParserToPostgreSQL
from src.base.Config import Constants
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTypes(DataTypesInternal):
    pass

class Operators(OperatorsInternal):
    pass

class BdTypes:
    SQLITE3 = 'sqlite'
    POSTGRESS = 'postgresql'

class BearSQL:
    def __init__(self, db_path: str, db_type: str = BdTypes.POSTGRESS):
        if not db_path:
            db_path = Constants.db_path

        self.db_path = db_path
        self.db_type = db_type
        
        operators = OperatorsInternal()
        
        if db_type == BdTypes.SQLITE3:
            parser = ParserToSqlite3(operators)
        elif db_type == BdTypes.POSTGRESS:
            parser = ParserToPostgreSQL(operators)
        else:
            parser = ParserToSqlite3(operators)
        
        self.adapter = Adapter(parser)
        
        self.ops = operators
    
    def _build_sql(self, *parts) -> str:
        sql_template = ' '.join(str(part) for part in parts if part)
        return self.adapter.adapt(sql_template)
    
    def save(self, table: str, data: dict) -> bool:
        Identifier._validate_identifier(table)
        for key in data.keys():
            Identifier._validate_identifier(key)
        
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([self.ops.PLACEHOLDER] * len(data))
            values = tuple(data.values())
            
            sql_template = f"""
                {self.ops.INSERT_INTO} {table} ({columns})
                {self.ops.VALUES} ({placeholders})
            """
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, values)
                gm.commit()
                return True
                
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    def get(self, columns: str = Operators.All, table: str = "", 
            where: dict = None, fetch_one: bool = False) -> Optional[Union[Tuple, List[Tuple]]]:
        if table:
            Identifier._validate_identifier(table)
        if columns != Operators.All:
            for col in columns.split(','):
                Identifier._validate_identifier(col.strip())
        
        try:
            sql_template = f"{self.ops.SELECT} {columns} {self.ops.FROM} {table}"
            
            params = []
            if where:
                conditions = []
                for key, value in where.items():
                    if '__' in key:
                        column, operator_suffix = key.split('__', 1)
                        operator_map = {
                            'gt': self.ops.GREATER,
                            'gte': self.ops.GREATER_EQUAL,
                            'lt': self.ops.LESS,
                            'lte': self.ops.LESS_EQUAL,
                            'eq': self.ops.EQUALS,
                            'ne': self.ops.NOT_EQUALS,
                            'like': self.ops.LIKE,
                            'ilike': 'ILIKE',
                            'in': self.ops.IN,
                            'isnull': self.ops.IS_NULL,
                            'isnotnull': self.ops.IS_NOT_NULL,
                        }
                        operator = operator_map.get(operator_suffix, self.ops.EQUALS)
                        
                        if operator in [self.ops.IS_NULL, self.ops.IS_NOT_NULL]:
                            conditions.append(f"{column} {operator}")
                        elif operator == self.ops.IN:
                            if not isinstance(value, (list, tuple)):
                                value = [value]
                            placeholders = ', '.join([self.ops.PLACEHOLDER] * len(value))
                            conditions.append(f"{column} {operator} ({placeholders})")
                            params.extend(value)
                        else:
                            conditions.append(f"{column} {operator} {self.ops.PLACEHOLDER}")
                            params.append(value)
                    elif isinstance(value, tuple) and len(value) == 2:
                        column, (operator, val) = key, value
                        conditions.append(f"{column} {operator} {self.ops.PLACEHOLDER}")
                        params.append(val)
                    else:
                        conditions.append(f"{key} {self.ops.EQUALS} {self.ops.PLACEHOLDER}")
                        params.append(value)
                
                where_clause = f" {self.ops.AND} ".join(conditions)
                sql_template += f" {self.ops.WHERE} {where_clause}"
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, params)
                
                if fetch_one:
                    result = gm.fetchone()
                else:
                    result = gm.fetchall()
                return result
                        
        except Exception as e:
            logger.error(f"Get error: {e}")
            return None

    
    def get_advanced(self, columns: str = Operators.All, table: str = "", 
                    where_conditions: list = None, fetch_one: bool = False) -> Optional[Union[Tuple, List[Tuple]]]:
        if table:
            Identifier._validate_identifier(table)
        if columns != Operators.All:
            for col in columns.split(','):
                Identifier._validate_identifier(col.strip())
        
        try: 
            sql_template = f"{self.ops.SELECT} {columns} {self.ops.FROM} {table}"
            
            params = []
            if where_conditions:
                conditions = []
                for number, cond in enumerate(where_conditions):
                    operator = cond.get('operator', self.ops.EQUALS)
                    value = cond['value']
                    
                    if operator == self.ops.IN:
                        if not isinstance(value, (list, tuple)):
                            value = [value]
                        placeholders = ', '.join([self.ops.PLACEHOLDER] * len(value))
                        conditions.append(f"{cond['column']} {operator} ({placeholders})")
                        params.extend(value)
                    else:
                        conditions.append(f"{cond['column']} {operator} {self.ops.PLACEHOLDER}")
                        params.append(value)
                    
                    if 'connector' in cond and number < len(where_conditions) - 1:
                        conditions.append(cond['connector'])
                
                where_clause = " ".join(conditions)
                sql_template += f" {self.ops.WHERE} {where_clause}"
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, params)
                
                if fetch_one:
                    result = gm.fetchone()
                else:
                    result = gm.fetchall()
                return result
                            
        except Exception as e:
            logger.error(f"Get advanced error: {e}")
            return None
    
    def create_table(self, table: str, schema: dict) -> bool:
        Identifier._validate_identifier(table)
        for col_name in schema.keys():
            Identifier._validate_identifier(col_name)
        
        try:
            columns_sql = []
            for col_name, sql_type in schema.items():
                columns_sql.append(f"{col_name} {sql_type}")
            
            columns_sql_str = ", ".join(columns_sql)
            
            sql_template = f"""
                {self.ops.CREATE_TABLE} {self.ops.IF_NOT_EXISTS} {table}
                ({columns_sql_str})
            """
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql)
                gm.commit()
                return True
                
        except Exception as e:
            logger.error(f"Create table error: {e}")
            return False
    
    def delete(self, table: str, where: dict) -> bool:
        Identifier._validate_identifier(table)
        
        try:
            conditions = []
            params = []
            
            for key, value in where.items():
                if '__' in key:
                    column, operator_suffix = key.split('__', 1)
                    operator_map = {
                        'gt': self.ops.GREATER,
                        'gte': self.ops.GREATER_EQUAL,
                        'lt': self.ops.LESS,
                        'lte': self.ops.LESS_EQUAL,
                        'eq': self.ops.EQUALS,
                        'ne': self.ops.NOT_EQUALS,
                    }
                    operator = operator_map.get(operator_suffix, self.ops.EQUALS)
                    conditions.append(f"{column} {operator} {self.ops.PLACEHOLDER}")
                    params.append(value)
                elif isinstance(value, tuple) and len(value) == 2:
                    column, (operator, val) = key, value
                    conditions.append(f"{column} {operator} {self.ops.PLACEHOLDER}")
                    params.append(val)
                else:
                    conditions.append(f"{key} {self.ops.EQUALS} {self.ops.PLACEHOLDER}")
                    params.append(value)
            
            where_clause = f" {self.ops.AND} ".join(conditions)
            
            sql_template = f"""
                {self.ops.DELETE_FROM} {table}
                {self.ops.WHERE} {where_clause}
            """
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, params)
                gm.commit()
                result = gm.get_rowcount() > 0
                return result
                
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    
    def save_and_get_id(self, table: str, data: dict) -> int:
        Identifier._validate_identifier(table)
        for key in data.keys():
            Identifier._validate_identifier(key)
        
        try: 
            columns = ', '.join(data.keys())
            placeholders = ', '.join([self.ops.PLACEHOLDER] * len(data))
            values = tuple(data.values())
            
            sql_template = f"""
                {self.ops.INSERT_INTO} {table} ({columns})
                {self.ops.VALUES} ({placeholders})
            """
            
            if self.db_type == 'postgresql':
                sql_template += " RETURNING id"
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, values)
                gm.commit()
                
                if self.db_type == 'postgresql':
                    result = gm.fetchone()
                    return result[0] if result else -1
                
                return gm.get_lastrowid()
                    
        except Exception as e:
            logger.error(f"Save error: {e}")
            return -1
    
    def execute_raw(self, sql_template: str, params: tuple = None) -> List[Tuple]:
        try:
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, params)
                if sql.strip().upper().startswith('SELECT'):
                    return gm.fetchall()
                else:
                    gm.commit()
                    return []
                    
        except Exception as e:
            logger.error(f"Execute raw error: {e}")
            return []
    
    def batch_insert(self, table: str, data_list: List[Dict]) -> bool:
        if not data_list:
            return False
        
        Identifier._validate_identifier(table)
        
        try:
            columns = list(data_list[0].keys())
            columns_str = ', '.join(columns)
            
            placeholders = ', '.join([self.ops.PLACEHOLDER] * len(columns))
            all_values = []
            values_placeholders = []
            
            for data in data_list:
                values = [data[col] for col in columns]
                all_values.extend(values)
                values_placeholders.append(f"({placeholders})")
            
            values_str = ', '.join(values_placeholders)
            
            sql_template = f"""
                {self.ops.INSERT_INTO} {table} ({columns_str})
                {self.ops.VALUES} {values_str}
            """
            
            sql = self.adapter.adapt(sql_template)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, tuple(all_values))
                gm.commit()
                return True
                
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            return False

    def advanced_update(self, table: str, data: dict, where_conditions: list = None) -> bool:
        if not table or not data:
            return False
            
        Identifier._validate_identifier(table)
        
        try:
            set_clauses = []
            params = []
            
            for column, value in data.items():
                Identifier._validate_identifier(column.strip())
                set_clauses.append(f"{column} = {self.ops.PLACEHOLDER}")
                params.append(value)
            
            set_sql = ", ".join(set_clauses)
            sql = f"{self.ops.UPDATE} {table} {self.ops.SET} {set_sql}"
            
            if where_conditions:
                where_sql, where_params = self._build_where_clause(where_conditions)
                sql += f" {self.ops.WHERE} {where_sql}"
                params.extend(where_params)
            
            sql = self.adapter.adapt(sql)
            
            with GeneralMethods(self.db_path) as gm:
                gm.execute(sql, params)
                gm.commit()
                return True
                
        except Exception as e:
            logger.error(f"Advanced update error: {e}")
            return False

    def _build_where_clause(self, conditions):
        where_parts = []
        params = []
        
        for i, cond in enumerate(conditions):
            column = cond['column']
            operator = cond.get('operator', self.ops.EQUALS)
            value = cond['value']
            
            Identifier._validate_identifier(column)
            
            if operator == self.ops.IN:
                if not isinstance(value, (list, tuple)):
                    value = [value]
                placeholders = ', '.join([self.ops.PLACEHOLDER] * len(value))
                where_parts.append(f"{column} {operator} ({placeholders})")
                params.extend(value)
            else:
                where_parts.append(f"{column} {operator} {self.ops.PLACEHOLDER}")
                params.append(value)
            
            if 'connector' in cond and i < len(conditions) - 1:
                where_parts.append(cond['connector'])
        
        return " ".join(where_parts), params