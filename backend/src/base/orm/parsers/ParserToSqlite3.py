from src.base.orm.parsers.SimpleParser import ParserTemplete
from typing import Dict

class ParserToSqlite3(ParserTemplete):
    def _build_replace_map(self) -> Dict[str, str]:
        ops = self.operators
        
        replace_map = {
            ops.SELECT: "SELECT",
            ops.FROM: "FROM", 
            ops.WHERE: "WHERE",
            ops.INSERT_INTO: "INSERT INTO",
            ops.VALUES: "VALUES",
            ops.UPDATE: "UPDATE",
            ops.SET: "SET",
            ops.DELETE_FROM: "DELETE FROM",
            ops.CREATE_TABLE: "CREATE TABLE",
            ops.IF_NOT_EXISTS: "IF NOT EXISTS",
            ops.UNION_ALL: "UNION ALL",
            
            ops.EQUALS: "=",
            ops.NOT_EQUALS: "!=",
            ops.GREATER: ">",
            ops.GREATER_EQUAL: ">=",
            ops.LESS: "<",
            ops.LESS_EQUAL: "<=",
            ops.BETWEEN: "BETWEEN",
            ops.NOT_BETWEEN: "NOT BETWEEN",
            
            ops.AND: "AND",
            ops.OR: "OR",
            ops.NOT: "NOT",
            ops.XOR: "XOR",
            
            ops.LIKE: "LIKE",
            ops.IN: "IN",
            ops.IS_NULL: "IS NULL",
            ops.IS_NOT_NULL: "IS NOT NULL",
            ops.EXISTS: "EXISTS",
            ops.NOT_EXISTS: "NOT EXISTS",
            
            ops.PLACEHOLDER: "?",
            ops.All: "*",
            
            ops.NOW(): "datetime('now')",
            ops.DATE_NOW(): "date('now')",
            ops.CURDATE: "date('now')",
            ops.CURTIME: "time('now')",
            ops.DATE_ADD: "datetime",
            ops.DATE_SUB: "datetime",
            ops.DATEDIFF: "julianday",
            ops.EXTRACT: "strftime",
            
            ops.SUM: "SUM",
            ops.COUNT: "COUNT",
            ops.AVG: "AVG",
            ops.MIN: "MIN",
            ops.MAX: "MAX",
            ops.GROUP_CONCAT: "group_concat",  
            ops.STDDEV: "stdev",
            ops.VARIANCE: "variance",
            
            ops.CONCAT: "||", 
            ops.SUBSTRING: "substr",
            ops.TRIM: "trim",
            ops.LTRIM: "ltrim",
            ops.RTRIM: "rtrim",
            ops.UPPER: "upper",
            ops.LOWER: "lower",
            ops.LENGTH: "length",
            ops.REPLACE: "replace",
            
            ops.ADD: "+",
            ops.SUBTRACT: "-",
            ops.MULTIPLY: "*",
            ops.DIVIDE: "/",
            ops.MODULO: "%",
            ops.POWER: "pow",
            ops.ABS: "abs",
            ops.ROUND: "round",
            ops.CEIL: "ceil",
            ops.FLOOR: "floor",
            
            ops.DISTINCT: "DISTINCT",
            ops.ORDER_BY: "ORDER BY",
            ops.GROUP_BY: "GROUP BY",
            ops.HAVING: "HAVING",
            ops.LIMIT: "LIMIT",
            ops.OFFSET: "OFFSET",
            ops.AS: "AS",
            
            ops.JOIN: "JOIN",
            ops.INNER_JOIN: "INNER JOIN",
            ops.LEFT_JOIN: "LEFT JOIN",
            ops.RIGHT_JOIN: "",
            ops.FULL_JOIN: "",  
            ops.CROSS_JOIN: "CROSS JOIN",
            ops.ON: "ON",
            ops.USING: "USING",
            
            ops.BEGIN: "BEGIN",
            ops.COMMIT: "COMMIT",
            ops.ROLLBACK: "ROLLBACK",
            ops.SAVEPOINT: "SAVEPOINT",
            ops.RELEASE_SAVEPOINT: "RELEASE SAVEPOINT",
            
            ops.ALTER_TABLE: "ALTER TABLE",
            ops.DROP_TABLE: "DROP TABLE",
            ops.TRUNCATE_TABLE: "DELETE FROM", 
            ops.ADD_COLUMN: "ADD COLUMN",
            ops.DROP_COLUMN: "DROP COLUMN",
            ops.RENAME_COLUMN: "RENAME COLUMN",
            ops.RENAME_TABLE: "RENAME TO",
            
            ops.CREATE_INDEX: "CREATE INDEX",
            ops.DROP_INDEX: "DROP INDEX",
            ops.UNIQUE_INDEX: "CREATE UNIQUE INDEX",
            
            ops.CASE: "CASE",
            ops.WHEN: "WHEN",
            ops.THEN: "THEN",
            ops.ELSE: "ELSE",
            ops.END: "END",
            ops.COALESCE: "coalesce",
            ops.NULLIF: "nullif",
            ops.CAST: "CAST",
            
            ops.JSON_EXTRACT: "json_extract",
            ops.JSON_SET: "json_set",
            ops.JSON_INSERT: "json_insert",
            ops.JSON_REPLACE: "json_replace",
            ops.JSON_REMOVE: "json_remove",
            ops.JSON_TYPE: "json_type",
            ops.JSON_VALID: "json_valid",
            
            ops.MATCH: "MATCH",
            ops.AGAINST: "",
            ops.IN_BOOLEAN_MODE: "",
            ops.IN_NATURAL_LANGUAGE_MODE: "",
            
            ops.OVER: "OVER",
            ops.PARTITION_BY: "PARTITION BY",
            ops.ROWS: "ROWS",
            ops.RANGE: "RANGE",
            ops.PRECEDING: "PRECEDING",
            ops.FOLLOWING: "FOLLOWING",
            ops.CURRENT_ROW: "CURRENT ROW",
            ops.UNBOUNDED: "UNBOUNDED",
            
            "ILIKE": "LIKE",
            "~~*": "LIKE",
            "!~~*": "NOT LIKE",
            "~": "REGEXP",
            "!~": "NOT REGEXP",
            "~*": "REGEXP",
            "!~*": "NOT REGEXP",
            
            "REGEXP": "REGEXP",
            "RLIKE": "REGEXP",
            "DIV": "/",
            "IFNULL(": "coalesce(",
            "IF(": "CASE WHEN ",
            
            "GETDATE()": "datetime('now')",
            "ISNULL(": "coalesce(",
            "TOP": "LIMIT",
            
            "SYSDATE": "datetime('now')",
            "NVL(": "coalesce(",
            "TO_DATE(": "date(",
            "TO_CHAR(": "CAST(",
        }
        
        return replace_map
    
    def _post_process(self, sql: str) -> str:
        result = sql
        
        if "RIGHT JOIN" in result.upper():
            result = result.replace("RIGHT JOIN", "LEFT JOIN")
        
        if "FULL JOIN" in result.upper():
            result = result.replace("FULL JOIN", "LEFT JOIN")
        
        if " XOR " in result.upper():
            import re
            pattern = r'([\w\.]+)\s+XOR\s+([\w\.]+)'
            
            def replace_xor(match):
                a, b = match.groups()
                return f"(({a} AND NOT {b}) OR (NOT {a} AND {b}))"
            
            result = re.sub(pattern, replace_xor, result, flags=re.IGNORECASE)
        
        if "MODIFY COLUMN" in result.upper():
            result = result.replace("MODIFY COLUMN", "")
        
        result = result.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        
        result = re.sub(r'ENGINE\s*=\s*\w+', '', result, flags=re.IGNORECASE)
        result = re.sub(r'CHARSET\s*=\s*\w+', '', result, flags=re.IGNORECASE)
        result = re.sub(r'DEFAULT CHARACTER SET \w+', '', result, flags=re.IGNORECASE)
        
        result = re.sub(r'COMMENT\s+\'.*?\'', '', result)
        
        type_replacements = {
            'TINYINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'MEDIUMINT': 'INTEGER',
            'BIGINT': 'INTEGER',
            'FLOAT': 'REAL',
            'DOUBLE': 'REAL',
            'DECIMAL': 'NUMERIC',
            'NUMERIC': 'NUMERIC',
            'DATETIME': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'YEAR': 'INTEGER',
            'ENUM': 'TEXT',
            'SET': 'TEXT',
            'MEDIUMTEXT': 'TEXT',
            'LONGTEXT': 'TEXT',
            'MEDIUMBLOB': 'BLOB',
            'LONGBLOB': 'BLOB',
        }
        
        for old_type, new_type in type_replacements.items():
            pattern = r'\b' + old_type + r'\b'
            result = re.sub(pattern, new_type, result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def _handle_date_functions(self, sql: str) -> str:
        import re
        
        pattern = r'DATE_ADD\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^ ]+)\s+([^)]+)\s*\)'
        
        def replace_date_add(match):
            column, interval, unit = match.groups()
            unit_map = {
                'DAY': 'day', 'DAYS': 'day',
                'MONTH': 'month', 'MONTHS': 'month',
                'YEAR': 'year', 'YEARS': 'year',
                'HOUR': 'hour', 'HOURS': 'hour',
                'MINUTE': 'minute', 'MINUTES': 'minute',
                'SECOND': 'second', 'SECONDS': 'second',
            }
            unit_lower = unit_map.get(unit.upper(), unit.lower())
            return f"datetime({column}, '+{interval} {unit_lower}')"
        
        sql = re.sub(pattern, replace_date_add, sql, flags=re.IGNORECASE)
        
        pattern = r'DATE_SUB\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^ ]+)\s+([^)]+)\s*\)'
        
        def replace_date_sub(match):
            column, interval, unit = match.groups()
            unit_map = {
                'DAY': 'day', 'DAYS': 'day',
                'MONTH': 'month', 'MONTHS': 'month',
                'YEAR': 'year', 'YEARS': 'year',
                'HOUR': 'hour', 'HOURS': 'hour',
                'MINUTE': 'minute', 'MINUTES': 'minute',
                'SECOND': 'second', 'SECONDS': 'second',
            }
            unit_lower = unit_map.get(unit.upper(), unit.lower())
            return f"datetime({column}, '-{interval} {unit_lower}')"
        
        sql = re.sub(pattern, replace_date_sub, sql, flags=re.IGNORECASE)
        
        pattern = r'EXTRACT\s*\(\s*([^ ]+)\s+FROM\s+([^)]+)\s*\)'
        
        def replace_extract(match):
            unit, column = match.groups()
            format_map = {
                'YEAR': '%Y',
                'MONTH': '%m',
                'DAY': '%d',
                'HOUR': '%H',
                'MINUTE': '%M',
                'SECOND': '%S',
            }
            fmt = format_map.get(unit.upper(), '%Y')
            return f"strftime('{fmt}', {column})"
        
        sql = re.sub(pattern, replace_extract, sql, flags=re.IGNORECASE)
        
        return sql