try:
    import psycopg
    print("Используем psycopg")
    PSYCOPG_VERSION = 3
    DATABASE_PARAM = "dbname"
    from psycopg import Connection as connection_class
    from psycopg import Cursor as cursor_class
except ImportError:
    try:
        import psycopg_binary as psycopg
        print("Используем psycopg_binary как psycopg")
        PSYCOPG_VERSION = 3
        DATABASE_PARAM = "dbname"
        from psycopg import Connection as connection_class
        from psycopg import Cursor as cursor_class
    except ImportError:
        try:
            import psycopg2 as psycopg
            print("Используем psycopg2 как psycopg")
            PSYCOPG_VERSION = 2
            DATABASE_PARAM = "database"
            from psycopg2.extensions import connection as connection_class
            from psycopg2.extensions import cursor as cursor_class
        except ImportError:
            raise ImportError("Нет драйвера PostgreSQL!")

psycopg2 = psycopg
connection = connection_class
cursor = cursor_class

from src.base.orm.ORMOptimizer import ConnectionPool
import re 
from typing import Optional, Tuple, Any, Dict, Union, List
from contextlib import contextmanager
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)

class GeneralMethodsMegaInternal:
    @staticmethod
    def parse_db_path(db_path: str) -> Dict[str, str]:
        if isinstance(db_path, str) and db_path.startswith('{'):
            try:
                import ast
                return ast.literal_eval(db_path)
            except:
                pass
        
        if db_path.startswith('postgresql://'):
            pattern = r'postgresql://(?:(.+?):(.+?)@)?([^:/]+)(?::(\d+))?/(.+)'
            match = re.match(pattern, db_path)
            if match:
                user, password, host, port, database = match.groups()
                return {
                    'user': user or 'postgres',
                    'password': password or '',
                    'host': host or 'localhost',
                    'port': port or '5432',
                    DATABASE_PARAM: database
                }
        
        elif '=' in db_path:
            params = {}
            for param in db_path.split():
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            if DATABASE_PARAM == "database" and "dbname" in params:
                params["database"] = params.pop("dbname")
            elif DATABASE_PARAM == "dbname" and "database" in params:
                params["dbname"] = params.pop("database")
            
            return params
        
        else:
            return {
                'host': 'localhost',
                'port': '5432',
                DATABASE_PARAM: db_path,
                'user': 'postgres',
                'password': ''
            }
    
    @staticmethod
    def _get_connection_params(db_path: Union[str, Dict]) -> Dict[str, str]:
        if isinstance(db_path, dict):
            params = db_path.copy()
        else:
            params = GeneralMethodsMegaInternal.parse_db_path(db_path)
        
        return params
    
    @staticmethod
    def get_connection(db_path: Union[str, Dict]) -> connection:
        try:
            params = GeneralMethodsMegaInternal._get_connection_params(db_path)
            
            if DATABASE_PARAM == "dbname":
                if "dbname" in params:
                    params["database"] = params["dbname"]
            
            conn = psycopg2.connect(**params)
            return conn
            
        except psycopg2.OperationalError as e:
            logging.error(f"PostgreSQL connection error: {e}")
            raise
        except Exception as e:
            logging.error(f"Connection error: {e}")
            raise
    
    def __init__(self, db_path: Union[str, Dict], use_pool: bool = True):
        self.db_path = db_path
        self.use_pool = use_pool
        self.connector: Optional[connection] = None
        self.cursor: Optional[cursor] = None
        self._pool = self._get_pool() if use_pool else None
        self._init_connection()
    
    def _init_connection(self):
        try:
            if self.use_pool and self._pool:
                if isinstance(self.db_path, dict):
                    params = self.db_path.copy()
                else:
                    params = GeneralMethodsMegaInternal.parse_db_path(self.db_path)
                
                if "dbname" in params:
                    params["database"] = params.pop("dbname")
                
                self.connector = self._pool.get_pool(params).getconn()
                
                pool_key = self._pool._get_pool_key(params)
                with self._pool._stats_lock:
                    if pool_key in self._pool._pool_metrics:
                        metrics = self._pool._pool_metrics[pool_key]
                        metrics['total_connections_created'] += 1
                        metrics['connections'][id(self.connector)] = datetime.now()
                
                logging.debug("PostgreSQL connection from pool")
            else:
                self.connector = GeneralMethodsMegaInternal.get_connection(self.db_path)
                logging.debug("PostgreSQL direct connection")
            
            self.connector.autocommit = False
            self.cursor = self.connector.cursor()
            
        except Exception as e:
            logging.error(f"Failed to initialize connection from pool: {e}")
            try:
                self.connector = GeneralMethodsMegaInternal.get_connection(self.db_path)
                self.connector.autocommit = False
                self.cursor = self.connector.cursor()
                logging.debug("Using direct connection as fallback")
            except Exception as e2:
                logging.error(f"Failed to initialize direct connection: {e2}")
                raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
    
    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None):
        if not self.cursor:
            raise RuntimeError("Cursor not initialized")
        
        try:
            safe_sql = sql
            if params:
                safe_sql = sql.replace('%s', '{}').format(*params)
            logging.debug(f"Executing SQL: {safe_sql}")
            
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
                
        except psycopg2.Error as e:
            logging.error(f"PostgreSQL error: {e}, SQL: {sql[:100]}...")
            raise
        except Exception as e:
            logging.error(f"Execute error: {e}, SQL: {sql[:100]}...")
            raise
    
    def commit(self):
        if self.connector:
            self.connector.commit()
            logging.debug("Changes committed")
    
    def rollback(self):
        if self.connector:
            self.connector.rollback()
            logging.debug("Changes rolled back")
    
    def begin_transaction(self):
        if self.cursor:
            self.cursor.execute("BEGIN")
            logging.debug("Transaction started")

    def execute_with_lock(self, sql: str, params: tuple = None, table: str = None):
        if not self.cursor:
            raise RuntimeError("Cursor not initialized")
        
        try:
            if table and 'SELECT' in sql.upper() and 'FOR UPDATE' not in sql.upper():
                sql = f"{sql.rstrip(';')} FOR UPDATE"
            
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
                
        except Exception as e:
            logging.error(f"Execute with lock error: {e}, SQL: {sql}")
            raise
    
    def fetchone(self):
        try:
            return self.cursor.fetchone() if self.cursor else None
        except Exception as e:
            logging.error(f"Fetchone error: {e}")
            return None
    
    def fetchall(self):
        try:
            if self.cursor and self.cursor.description is not None:
                return self.cursor.fetchall()
            return []
        except Exception as e:
            logging.error(f"Fetchall error: {e}")
            return []
    
    def get_lastrowid(self):
        if not self.cursor:
            return None
        try:
            self.cursor.execute("SELECT lastval()")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Get lastrowid error: {e}")
            return None
    
    def get_rowcount(self):
        return self.cursor.rowcount if self.cursor else -1
    
    def close_connection(self):
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            
            if self.connector:
                if self.use_pool and self._pool:
                    try:
                        if not self.connector.autocommit:
                            self.connector.rollback()
                        
                        if isinstance(self.db_path, dict):
                            params = self.db_path.copy()
                        else:
                            params = GeneralMethodsMegaInternal.parse_db_path(self.db_path)
                        
                        if "dbname" in params:
                            params["database"] = params.pop("dbname")
                        
                        pool_key = self._pool._get_pool_key(params)
                        self._pool.get_pool(params).putconn(self.connector)
                        
                        with self._pool._stats_lock:
                            if pool_key in self._pool._pool_metrics:
                                self._pool._pool_metrics[pool_key]['connections_returned'] += 1
                        
                        logging.debug("Connection returned to pool")
                        
                    except Exception as e:
                        logging.error(f"Error returning connection to pool: {e}")
                        self.connector.close()
                else:
                    self.connector.close()
                
                self.connector = None
                
        except Exception as e:
            logging.error(f"Close connection error: {e}")
    
    def create_database(self, dbname: str) -> bool:
        try:
            system_params = {
                'host': 'localhost',
                'port': '5432',
                DATABASE_PARAM: 'postgres',
                'user': 'postgres',
                'password': ''
            }
            
            if isinstance(self.db_path, dict):
                for key, value in self.db_path.items():
                    if key not in [DATABASE_PARAM, 'dbname', 'database']:
                        system_params[key] = value
            
            conn = psycopg2.connect(**system_params)
            conn.autocommit = True
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{dbname}"')
                logging.info(f"Database '{dbname}' created")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Create database error: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        try:
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table_name,))
            result = self.cursor.fetchone()
            return result[0] if result else False
        except Exception as e:
            logging.error(f"Table exists check error: {e}")
            return False
    
    def health_check(self) -> bool:
        try:
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            return result[0] == 1 if result else False
        except Exception:
            return False

    @classmethod
    def _get_pool(cls):
        return None


class GeneralMethods(GeneralMethodsMegaInternal):
    
    _connection_pool = None
    
    @classmethod
    def _get_pool(cls):
        if cls._connection_pool is None:
            cls._connection_pool = ConnectionPool(
                min_conn=3, 
                max_conn=10,
                idle_timeout=300,
                max_lifetime=1800
            )
        return cls._connection_pool
    
    @staticmethod
    def parse_db_path(db_path: str) -> Dict[str, str]:
        return GeneralMethodsMegaInternal.parse_db_path(db_path)
    
    @staticmethod
    def get_connection(db_path: Union[str, Dict]) -> connection:
        try:
            if isinstance(db_path, dict):
                params = db_path.copy()
            else:
                params = GeneralMethods.parse_db_path(db_path)
            
            if "dbname" in params:
                params["database"] = params.pop("dbname")
            
            pool = GeneralMethods._get_pool()
            conn = pool.get_pool(params).getconn()
            conn.autocommit = False
            
            return conn
            
        except Exception as e:
            logging.error(f"Connection pool error: {e}")
            return GeneralMethodsMegaInternal.get_connection(db_path)
    
    def __init__(self, db_path: Union[str, Dict], use_pool: bool = True):
        super().__init__(db_path, use_pool)
    
    @classmethod
    def get_pool_stats(cls):
        pool = cls._get_pool()
        return pool.get_stats()
    
    @classmethod
    def close_pool(cls):
        if cls._connection_pool:
            cls._connection_pool.close_all()
            cls._connection_pool = None



class DataTypesInternal:
    INT = "INTEGER"
    FLOAT = "REAL" 
    STRING = "TEXT"
    BOOL = "BOOLEAN"
    DATETIME = "DATETIME"
    ID = "INTEGER PRIMARY KEY AUTOINCREMENT"
    MONEY = "REAL"
    EMAIL = "TEXT"
    JSON = "TEXT"

    @staticmethod
    def DECIMAL(precision: int = 10, scale: int = 2) -> str:
        return f"NUMERIC({precision}, {scale})"
    
    @staticmethod
    def with_default(data_type: str, default_value: str) -> str:
        return f"{data_type} DEFAULT {default_value}"

class OperatorsInternal:
    AND = "AND"
    OR = "OR" 
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    LIKE = "LIKE"
    IN = "IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    PLACEHOLDER = "?"
    All = "*"

    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT_INTO = "INSERT INTO"
    UPDATE = "UPDATE"
    DELETE_FROM = "DELETE FROM"
    CREATE_TABLE = "CREATE TABLE"
    IF_NOT_EXISTS = "IF NOT EXISTS"
    VALUES = "VALUES"
    SET = "SET"
    UNION_ALL = "UNION ALL"

    SUM = "SUM"
    COUNT = "COUNT"
    DATE = "DATE"
    DATETIME = "DATETIME"
    
    NOT = "NOT"
    XOR = "XOR"
    
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT EXISTS"
    
    CONCAT = "CONCAT"
    SUBSTRING = "SUBSTRING"
    TRIM = "TRIM"
    LTRIM = "LTRIM"
    RTRIM = "RTRIM"
    UPPER = "UPPER"
    LOWER = "LOWER"
    LENGTH = "LENGTH"
    REPLACE = "REPLACE"
    
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "POWER"
    ABS = "ABS"
    ROUND = "ROUND"
    CEIL = "CEIL"
    FLOOR = "FLOOR"
    
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    GROUP_CONCAT = "GROUP_CONCAT"
    STDDEV = "STDDEV"
    VARIANCE = "VARIANCE"
    
    NOW = "NOW"
    CURDATE = "CURDATE"
    CURTIME = "CURTIME"
    DATE_ADD = "DATE_ADD"
    DATE_SUB = "DATE_SUB"
    DATEDIFF = "DATEDIFF"
    EXTRACT = "EXTRACT"
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"
    
    DISTINCT = "DISTINCT"
    ORDER_BY = "ORDER BY"
    GROUP_BY = "GROUP BY"
    HAVING = "HAVING"
    LIMIT = "LIMIT"
    OFFSET = "OFFSET"
    AS = "AS"
    ON = "ON"
    JOIN = "JOIN"
    INNER_JOIN = "INNER JOIN"
    LEFT_JOIN = "LEFT JOIN"
    RIGHT_JOIN = "RIGHT JOIN"
    FULL_JOIN = "FULL JOIN"
    CROSS_JOIN = "CROSS JOIN"
    USING = "USING"
    
    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    SAVEPOINT = "SAVEPOINT"
    RELEASE_SAVEPOINT = "RELEASE SAVEPOINT"
    
    ALTER_TABLE = "ALTER TABLE"
    DROP_TABLE = "DROP TABLE"
    TRUNCATE_TABLE = "TRUNCATE TABLE"
    ADD_COLUMN = "ADD COLUMN"
    DROP_COLUMN = "DROP COLUMN"
    MODIFY_COLUMN = "MODIFY COLUMN"
    RENAME_COLUMN = "RENAME COLUMN"
    RENAME_TABLE = "RENAME TABLE"
    
    CREATE_INDEX = "CREATE INDEX"
    DROP_INDEX = "DROP INDEX"
    UNIQUE_INDEX = "UNIQUE INDEX"
    
    OVER = "OVER"
    PARTITION_BY = "PARTITION BY"
    ROWS = "ROWS"
    RANGE = "RANGE"
    PRECEDING = "PRECEDING"
    FOLLOWING = "FOLLOWING"
    CURRENT_ROW = "CURRENT ROW"
    UNBOUNDED = "UNBOUNDED"
    
    CASE = "CASE"
    WHEN = "WHEN"
    THEN = "THEN"
    ELSE = "ELSE"
    END = "END"
    COALESCE = "COALESCE"
    NULLIF = "NULLIF"
    CAST = "CAST"
    
    JSON_EXTRACT = "JSON_EXTRACT"
    JSON_SET = "JSON_SET"
    JSON_INSERT = "JSON_INSERT"
    JSON_REPLACE = "JSON_REPLACE"
    JSON_REMOVE = "JSON_REMOVE"
    JSON_TYPE = "JSON_TYPE"
    JSON_VALID = "JSON_VALID"
    
    MATCH = "MATCH"
    AGAINST = "AGAINST"
    IN_BOOLEAN_MODE = "IN BOOLEAN MODE"
    IN_NATURAL_LANGUAGE_MODE = "IN NATURAL LANGUAGE MODE"

    PRIMARY_KEY = "PRIMARY KEY"
    UNIQUE = "UNIQUE"
    DEFAULT = "DEFAULT"
    CHECK = "CHECK"
    FOREIGN_KEY = "FOREIGN KEY"
    REFERENCES = "REFERENCES"
    CONSTRAINT = "CONSTRAINT"

    SERIAL = "SERIAL"
    BIGSERIAL = "BIGSERIAL"
    JSONB = "JSONB"
    TEXT_ARRAY = "TEXT[]"
    INTEGER_ARRAY = "INTEGER[]"

    NULL = "NULL"
    NOT_NULL = "NOT NULL"
    AUTO_INCREMENT = "AUTO_INCREMENT"
    CURRENT_TIMESTAMP = "CURRENT_TIMESTAMP"
    CURRENT_DATE = "CURRENT_DATE"

    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT EXISTS"
    ALL = "ALL"
    ANY = "ANY"
    SOME = "SOME"

    ASC = "ASC"
    DESC = "DESC"

    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    SAVEPOINT = "SAVEPOINT"

    CREATE_INDEX = "CREATE INDEX"
    DROP_INDEX = "DROP INDEX"
    UNIQUE_INDEX = "UNIQUE INDEX"
    
    FOR = "FOR"
    
    @staticmethod
    def NOW() -> str:
        return "datetime('now')"
    
    @staticmethod  
    def DATE_NOW() -> str:
        return "DATE('now')"
    
    @staticmethod
    def DATETIME_ADD(days: int) -> str:
        return f"datetime('now', '+{days} days')"
    
    @staticmethod
    def LAST_INSERT_ID() -> str:
        return "last_insert_rowid()"
    
    @staticmethod
    def AVG(column: str) -> str:
        return f"AVG({column})"
    
    @staticmethod
    def MAX(column: str) -> str:
        return f"MAX({column})"
    
    @staticmethod
    def MIN(column: str) -> str:
        return f"MIN({column})"
    
    @staticmethod
    def CONCAT(*args: str) -> str:
        columns = ', '.join(args)
        return f"CONCAT({columns})"
    
    @staticmethod
    def SUBSTRING(column: str, start: int, length: int = None) -> str:
        if length:
            return f"SUBSTRING({column}, {start}, {length})"
        return f"SUBSTRING({column}, {start})"
    
    @staticmethod
    def COUNT_DISTINCT(column: str) -> str:
        return f"COUNT(DISTINCT {column})"
    
    @staticmethod
    def IF_NULL(column: str, default_value: str) -> str:
        return f"IFNULL({column}, {default_value})"
    
    @staticmethod
    def CASE_WHEN(condition: str, then_value: str, else_value: str = None) -> str:
        sql = f"CASE WHEN {condition} THEN {then_value}"
        if else_value:
            sql += f" ELSE {else_value}"
        sql += " END"
        return sql
    
    @staticmethod
    def CAST(column: str, target_type: str) -> str:
        return f"CAST({column} AS {target_type})"
    
    @staticmethod
    def JSON_EXTRACT_PATH(column: str, path: str) -> str:
        return f"JSON_EXTRACT({column}, '$.{path}')"
    
    ALLOWED_OPERATORS = {
        AND, OR, EQUALS, NOT_EQUALS, 
        GREATER, GREATER_EQUAL, LESS, LESS_EQUAL, 
        LIKE, IN, IS_NULL, IS_NOT_NULL,
        "<", ">", "<=", ">=", "=", "!=",
        
        NOT, XOR, BETWEEN, NOT_BETWEEN, EXISTS, NOT_EXISTS,
        CONCAT, SUBSTRING, TRIM, LTRIM, RTRIM, UPPER, LOWER,
        LENGTH, REPLACE, ADD, SUBTRACT, MULTIPLY, DIVIDE,
        MODULO, POWER, ABS, ROUND, CEIL, FLOOR,
        AVG, MIN, MAX, GROUP_CONCAT, STDDEV, VARIANCE,
        DISTINCT, ORDER_BY, GROUP_BY, HAVING, LIMIT, OFFSET,
        AS, ON, JOIN, INNER_JOIN, LEFT_JOIN, RIGHT_JOIN,
        FULL_JOIN, CROSS_JOIN, USING,
        CASE, WHEN, THEN, ELSE, END, COALESCE, NULLIF, CAST,
        MATCH, AGAINST
    }

    RETURNING = "RETURNING"
    DESC = "DESC"
    ASC = "ASC"
    
    @staticmethod
    def DATE_ADD_FUNC(column: str, interval: str, unit: str) -> str:
        return f"DATE_ADD({column}, INTERVAL {interval} {unit})"
    
    @staticmethod
    def DATE_SUB_FUNC(column: str, interval: str, unit: str) -> str:
        return f"DATE_SUB({column}, INTERVAL {interval} {unit})"
    
    @staticmethod
    def IF(condition: str, true_value: str, false_value: str = None) -> str:
        if false_value:
            return f"IF({condition}, {true_value}, {false_value})"
        return f"IF({condition}, {true_value})"
    
    @staticmethod  
    def GROUP_CONCAT_FUNC(column: str, separator: str = ',') -> str:
        return f"GROUP_CONCAT({column}, '{separator}')"

class Identifier:
    @staticmethod
    def _validate_identifier(identifier: str) -> str:
        if not identifier or identifier.isspace():
            return identifier
            
        if any(keyword in identifier.upper() for keyword in ['JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'OUTER JOIN', 'FULL JOIN']):
            return identifier
            
        if ' ON ' in identifier.upper():
            return identifier
            
        if ' AS ' in identifier.upper():
            return identifier
            
        if '(' in identifier and ')' in identifier:
            return identifier
            
        if '.' in identifier:
            parts = identifier.split('.')
            for part in parts:
                part = part.strip()
                if not part:
                    raise ValueError(f"Invalid SQL identifier (empty part): {identifier}")
                if ' AS ' in part.upper():
                    alias_parts = part.split(' AS ', 1)
                    for alias_part in alias_parts:
                        clean_alias = alias_part.strip().replace('"', '').replace("'", "")
                        if not clean_alias.replace('_', '').isalnum() and clean_alias != '*':
                            raise ValueError(f"Invalid SQL identifier part in alias: {alias_part} in {identifier}")
                    continue
                clean_part = part.strip().replace('"', '').replace("'", "")
                if not clean_part.replace('_', '').replace('.', '').isalnum() and clean_part != '*':
                    raise ValueError(f"Invalid SQL identifier part: {part} in {identifier}")
            return identifier
            
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP BY', 
                       'ORDER BY', 'LIMIT', 'OFFSET']
            
        if identifier.upper() in sql_keywords:
            return identifier

        if '(' in identifier and ')' in identifier:
            func_name = identifier.split('(')[0].strip()
            if func_name:
                if not func_name.replace('_', '').replace('"', '').isalnum():
                    raise ValueError(f"Invalid SQL function name: {func_name}")
            return identifier
        else:
            clean_id = identifier.strip().replace('"', '').replace("'", "")
            if clean_id == '*':
                return identifier
            if any(op in clean_id for op in ['+', '-', '*', '/', '%']):
                return identifier
            if not clean_id.replace('_', '').isalnum():
                raise ValueError(f"Invalid SQL identifier: {identifier}")
            return identifier
    
    @staticmethod
    def _escape_identifier(identifier: str) -> str:
        validated = Identifier._validate_identifier(identifier)
        
        if (validated.startswith('"') or 
            '.' in validated or
            ' AS ' in validated.upper() or
            ' JOIN ' in validated.upper() or
            ' ON ' in validated.upper() or
            '(' in validated or
            validated in ['*', 'COUNT(*)', 'SUM(*)']):
            return validated
            
        if validated.startswith('"') and validated.endswith('"'):
            return validated
            
        return f'"{validated}"'