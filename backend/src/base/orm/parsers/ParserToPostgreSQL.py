from src.base.orm.parsers.SimpleParser import ParserTemplete
from typing import Dict
import re

class ParserToPostgreSQL(ParserTemplete):    
    def _build_replace_map(self) -> Dict[str, str]:
        ops = self.operators
        
        return {
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
            ops.XOR: "#",

            ops.LIKE: "LIKE",
            "ILIKE": "ILIKE",
            ops.IN: "IN",
            ops.IS_NULL: "IS NULL",
            ops.IS_NOT_NULL: "IS NOT NULL",
            ops.EXISTS: "EXISTS",
            ops.NOT_EXISTS: "NOT EXISTS",

            ops.PLACEHOLDER: "%s",
            ops.All: "*",

            ops.NOW(): "NOW()",
            ops.DATE_NOW(): "CURRENT_DATE",
            ops.CURDATE: "CURRENT_DATE",
            ops.CURTIME: "CURRENT_TIME",
            ops.DATE_ADD: "interval",
            ops.DATE_SUB: "interval",
            ops.DATEDIFF: "DATE_PART",
            ops.EXTRACT: "EXTRACT",

            ops.SUM: "SUM",
            ops.COUNT: "COUNT",
            ops.AVG: "AVG",
            ops.MIN: "MIN",
            ops.MAX: "MAX",
            ops.GROUP_CONCAT: "STRING_AGG",
            ops.STDDEV: "STDDEV",
            ops.VARIANCE: "VARIANCE",

            ops.CONCAT: "||",
            ops.SUBSTRING: "SUBSTRING",
            ops.TRIM: "TRIM",
            ops.LTRIM: "LTRIM",
            ops.RTRIM: "RTRIM",
            ops.UPPER: "UPPER",
            ops.LOWER: "LOWER",
            ops.LENGTH: "LENGTH",
            ops.REPLACE: "REPLACE",

            ops.ADD: "+",
            ops.SUBTRACT: "-",
            ops.MULTIPLY: "*",
            ops.DIVIDE: "/",
            ops.MODULO: "%",
            ops.POWER: "POWER",
            ops.ABS: "ABS",
            ops.ROUND: "ROUND",
            ops.CEIL: "CEIL",
            ops.FLOOR: "FLOOR",

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
            ops.RIGHT_JOIN: "RIGHT JOIN",
            ops.FULL_JOIN: "FULL JOIN",
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
            ops.TRUNCATE_TABLE: "TRUNCATE TABLE",
            ops.ADD_COLUMN: "ADD COLUMN",
            ops.DROP_COLUMN: "DROP COLUMN",
            ops.MODIFY_COLUMN: "ALTER COLUMN TYPE",
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
            ops.COALESCE: "COALESCE",
            ops.NULLIF: "NULLIF",
            ops.CAST: "CAST",

            ops.JSON_EXTRACT: "->>",
            "JSON_EXTRACT_OBJECT": "->",
            ops.JSON_SET: "jsonb_set",
            ops.JSON_INSERT: "jsonb_insert",
            ops.JSON_REPLACE: "jsonb_set",
            ops.JSON_REMOVE: "jsonb_delete",
            ops.JSON_TYPE: "jsonb_typeof",
            ops.JSON_VALID: "jsonb_valid",

            ops.MATCH: "@@",
            ops.AGAINST: "to_tsvector",
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

            "ARRAY": "ARRAY",
            "ARRAY_AGG": "ARRAY_AGG",
            "UNNEST": "UNNEST",
            "ANY": "ANY",
            "ALL": "ALL",
            "ARRAY_LENGTH": "ARRAY_LENGTH",

            "ST_Distance": "ST_Distance",
            "ST_Contains": "ST_Contains",
            "ST_Intersects": "ST_Intersects",

            "datetime('now')": "NOW()",
            "date('now')": "CURRENT_DATE",
            "last_insert_rowid()": "LASTVAL()",
            "AUTOINCREMENT": "GENERATED BY DEFAULT AS IDENTITY",

            "REGEXP": "~",
            "RLIKE": "~",
            "IFNULL(": "COALESCE(",
            "IF(": "CASE WHEN ",
            "ENGINE=InnoDB": "",
            "CHARSET=utf8mb4": "",

            "GETDATE()": "NOW()",
            "ISNULL(": "COALESCE(",
            "TOP": "LIMIT",

            "SYSDATE": "NOW()",
            "NVL(": "COALESCE(",
            "TO_DATE(": "TO_DATE(",
            "TO_CHAR(": "TO_CHAR(",
        }
    
    def _post_process(self, sql: str) -> str:
        import re
        result = sql

        if result.upper().startswith("INSERT INTO") and "RETURNING" not in result.upper():
            if ")" in result:
                result = result.rstrip() + " RETURNING id"

        type_replacements = {
            'INTEGER PRIMARY KEY AUTOINCREMENT': 'SERIAL PRIMARY KEY',
            'AUTOINCREMENT': 'GENERATED BY DEFAULT AS IDENTITY',
            'TEXT': 'VARCHAR',
            'BLOB': 'BYTEA',
            'REAL': 'DOUBLE PRECISION',
            'NUMERIC': 'NUMERIC',
            'DATETIME': 'TIMESTAMP',
            'BOOLEAN': 'BOOLEAN',
        }
        
        for old_type, new_type in type_replacements.items():
            pattern = r'\b' + re.escape(old_type) + r'\b'
            result = re.sub(pattern, new_type, result, flags=re.IGNORECASE)

        result = self._handle_date_functions(result)

        result = self._handle_json_functions(result)

        result = result.replace('`', '"')

        result = re.sub(r'ENGINE\s*=\s*\w+', '', result, flags=re.IGNORECASE)
        result = re.sub(r'CHARSET\s*=\s*\w+', '', result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def _handle_date_functions(self, sql: str) -> str:
        import re

        pattern = r'DATE_ADD\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^ ]+)\s+([^)]+)\s*\)'
        
        def replace_date_add(match):
            column, interval, unit = match.groups()
            return f"{column} + INTERVAL '{interval} {unit}'"
        
        sql = re.sub(pattern, replace_date_add, sql, flags=re.IGNORECASE)

        pattern = r'DATE_SUB\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^ ]+)\s+([^)]+)\s*\)'
        
        def replace_date_sub(match):
            column, interval, unit = match.groups()
            return f"{column} - INTERVAL '{interval} {unit}'"
        
        sql = re.sub(pattern, replace_date_sub, sql, flags=re.IGNORECASE)

        pattern = r'DATEDIFF\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
        
        def replace_datediff(match):
            unit, start, end = match.groups()
            return f"DATE_PART('{unit}', {end} - {start})"
        
        sql = re.sub(pattern, replace_datediff, sql, flags=re.IGNORECASE)
        
        return sql
    
    def _handle_json_functions(self, sql: str) -> str:
        import re

        pattern = r'JSON_EXTRACT\s*\(\s*([^,]+)\s*,\s*\'\$\.([^\']+)\'\s*\)'
        
        def replace_json_extract(match):
            column, path = match.groups()
            return f"{column}->>'{path}'"
        
        sql = re.sub(pattern, replace_json_extract, sql, flags=re.IGNORECASE)

        pattern = r'JSON_EXTRACT_OBJECT\s*\(\s*([^,]+)\s*,\s*\'\$\.([^\']+)\'\s*\)'
        
        def replace_json_object(match):
            column, path = match.groups()
            return f"{column}->'{path}'"
        
        sql = re.sub(pattern, replace_json_object, sql, flags=re.IGNORECASE)
        
        return sql
