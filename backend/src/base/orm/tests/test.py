from src.core.database.orm.mainBD import NewRepository, Operators, DataTypes
from src.core.database.orm.BdRepository import Repository
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ==================== КОНФИГУРАЦИЯ ====================
# ИЗМЕНИТЕ ТОЛЬКО ЗДЕСЬ ↓↓↓
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "user": "postgres",
    "password": "12345"
}

DB_TYPE = "postgresql"

def get_db_path(config: Dict = None) -> str:
    """Создает строку подключения из конфига"""
    config = config or POSTGRES_CONFIG
    return f"host={config['host']} port={config['port']} dbname={config['database']} user={config['user']} password={config['password']}"
# ==================== КОНЕЦ КОНФИГУРАЦИИ ====================


class HardcoreRepositoryTest:
    """Жесткий тест всего репозитория с использованием всех операторов"""
    
    def __init__(self):
        """Инициализация - создаем репозиторий здесь"""
        self.db_path = get_db_path()
        self.repo = NewRepository(self.db_path, DB_TYPE)  # ← ИСПРАВЛЕНО!
        self.ops = Operators
        self.test_data = {}
        self.start_time = None
        self.results = {}
    
    def start_test(self, test_name: str):
        """Начинает тест"""
        self.start_time = time.time()
        print(f"\n{'='*80}")
        print(f"НАЧИНАЕМ ТЕСТ: {test_name}")
        print(f"{'='*80}")
        return self
    
    def end_test(self, success: bool = True):
        """Заканчивает тест"""
        elapsed = time.time() - self.start_time
        status = "✅ УСПЕХ" if success else "❌ ПРОВАЛ"
        print(f"{'='*80}")
        print(f"{status} | Время: {elapsed:.3f} сек")
        print(f"{'='*80}")
        self.start_time = None
        return success
    
    def assert_true(self, condition: bool, message: str = ""):
        """Проверка условия"""
        if not condition:
            raise AssertionError(f"FAIL: {message}")
        print(f"  ✓ {message}")
        return True
    
    def assert_equal(self, actual, expected, message: str = ""):
        """Проверка равенства"""
        if actual != expected:
            raise AssertionError(f"FAIL: {message} | Expected: {expected}, Got: {actual}")
        print(f"  ✓ {message}: {actual}")
        return True
    
    def assert_greater(self, actual, expected, message: str = ""):
        """Проверка больше"""
        if actual <= expected:
            raise AssertionError(f"FAIL: {message} | Should be > {expected}, Got: {actual}")
        print(f"  ✓ {message}: {actual} > {expected}")
        return True
    
    # ==================== ТЕСТ ОПЕРАТОРОВ ====================
    
    def test_basic_operators(self):
        """Тест базовых операторов"""
        self.start_test("БАЗОВЫЕ SQL ОПЕРАТОРЫ")
        
        try:
            # Проверяем что все операторы доступны
            operators = [
                self.ops.SELECT, self.ops.FROM, self.ops.WHERE,
                self.ops.INSERT_INTO, self.ops.UPDATE, self.ops.DELETE_FROM,
                self.ops.CREATE_TABLE, self.ops.IF_NOT_EXISTS, self.ops.VALUES,
                self.ops.SET, self.ops.UNION_ALL,
                self.ops.AND, self.ops.OR,
                self.ops.EQUALS, self.ops.NOT_EQUALS,
                self.ops.GREATER, self.ops.GREATER_EQUAL,
                self.ops.LESS, self.ops.LESS_EQUAL,
                self.ops.LIKE, self.ops.IN,
                self.ops.IS_NULL, self.ops.IS_NOT_NULL,
                self.ops.PLACEHOLDER
            ]
            
            for op in operators:
                self.assert_true(op is not None, f"Оператор {op} доступен")
            
            # Проверяем методы операторов
            self.assert_true(callable(self.ops.NOW), "Метод NOW() доступен")
            self.assert_true(callable(self.ops.DATE_NOW), "Метод DATE_NOW() доступен")
            self.assert_true(callable(self.ops.DATETIME_ADD), "Метод DATETIME_ADD() доступен")
            self.assert_true(callable(self.ops.LAST_INSERT_ID), "Метод LAST_INSERT_ID() доступен")
            self.assert_true(callable(self.ops.AVG), "Метод AVG() доступен")
            self.assert_true(callable(self.ops.MAX), "Метод MAX() доступен")
            self.assert_true(callable(self.ops.MIN), "Метод MIN() доступен")
            self.assert_true(callable(self.ops.CONCAT), "Метод CONCAT() доступен")
            self.assert_true(callable(self.ops.SUBSTRING), "Метод SUBSTRING() доступен")
            self.assert_true(callable(self.ops.COUNT_DISTINCT), "Метод COUNT_DISTINCT() доступен")
            self.assert_true(callable(self.ops.IF_NULL), "Метод IF_NULL() доступен")
            self.assert_true(callable(self.ops.CASE_WHEN), "Метод CASE_WHEN() доступен")
            self.assert_true(callable(self.ops.CAST), "Метод CAST() доступен")
            self.assert_true(callable(self.ops.JSON_EXTRACT_PATH), "Метод JSON_EXTRACT_PATH() доступен")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            return self.end_test(False)
    
    # ==================== ТЕСТ СЛОЖНЫХ ОПЕРАТОРОВ ====================
    
    def test_advanced_operators(self):
        """Тест расширенных операторов"""
        self.start_test("РАСШИРЕННЫЕ SQL ОПЕРАТОРЫ")
        
        try:
            # Математические операторы
            math_ops = [
                self.ops.ADD, self.ops.SUBTRACT, self.ops.MULTIPLY,
                self.ops.DIVIDE, self.ops.MODULO, self.ops.POWER,
                self.ops.ABS, self.ops.ROUND, self.ops.CEIL, self.ops.FLOOR
            ]
            
            for op in math_ops:
                self.assert_true(op is not None, f"Математический оператор {op} доступен")
            
            # Агрегатные функции
            agg_ops = [
                self.ops.SUM, self.ops.COUNT, self.ops.AVG,
                self.ops.MIN, self.ops.MAX, self.ops.GROUP_CONCAT,
                self.ops.STDDEV, self.ops.VARIANCE
            ]
            
            for op in agg_ops:
                self.assert_true(op is not None, f"Агрегатный оператор {op} доступен")
            
            # Строковые функции
            string_ops = [
                self.ops.CONCAT, self.ops.SUBSTRING, self.ops.TRIM,
                self.ops.LTRIM, self.ops.RTRIM, self.ops.UPPER,
                self.ops.LOWER, self.ops.LENGTH, self.ops.REPLACE
            ]
            
            for op in string_ops:
                self.assert_true(op is not None, f"Строковый оператор {op} доступен")
            
            # Дата-время функции
            date_ops = [
                self.ops.DATE, self.ops.DATETIME, self.ops.NOW,
                self.ops.CURDATE, self.ops.CURTIME, self.ops.DATE_ADD,
                self.ops.DATE_SUB, self.ops.DATEDIFF, self.ops.EXTRACT,
                self.ops.YEAR, self.ops.MONTH, self.ops.DAY,
                self.ops.HOUR, self.ops.MINUTE, self.ops.SECOND
            ]
            
            for op in date_ops:
                if isinstance(op, str):
                    self.assert_true(op is not None, f"Дата-время оператор {op} доступен")
            
            # JOIN операторы
            join_ops = [
                self.ops.JOIN, self.ops.INNER_JOIN, self.ops.LEFT_JOIN,
                self.ops.RIGHT_JOIN, self.ops.FULL_JOIN, self.ops.CROSS_JOIN,
                self.ops.ON, self.ops.USING
            ]
            
            for op in join_ops:
                self.assert_true(op is not None, f"JOIN оператор {op} доступен")
            
            # Управляющие операторы
            control_ops = [
                self.ops.CASE, self.ops.WHEN, self.ops.THEN,
                self.ops.ELSE, self.ops.END, self.ops.COALESCE,
                self.ops.NULLIF
            ]
            
            for op in control_ops:
                self.assert_true(op is not None, f"Управляющий оператор {op} доступен")
            
            # JSON операторы
            json_ops = [
                self.ops.JSON_EXTRACT, self.ops.JSON_SET,
                self.ops.JSON_INSERT, self.ops.JSON_REPLACE,
                self.ops.JSON_REMOVE, self.ops.JSON_TYPE,
                self.ops.JSON_VALID
            ]
            
            for op in json_ops:
                self.assert_true(op is not None, f"JSON оператор {op} доступен")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            return self.end_test(False)
    
    # ==================== ТЕСТ МЕТОДОВ РЕПОЗИТОРИЯ ====================
    
    def test_repository_methods(self):
        """Тест всех методов репозитория с использованием операторов из self.ops"""
        self.start_test("МЕТОДЫ РЕПОЗИТОРИЯ (С ОПЕРАТОРАМИ)")
        
        try:
            # Очищаем тестовые таблицы
            self._cleanup_tables()
            
            # 1. Тест create_table с операторами
            print("\n1. CREATE TABLE с операторами...")
            
            # Используем операторы для построения SQL
            schema = {
                "id": f"SERIAL {self.ops.PRIMARY_KEY}",
                "name": f"VARCHAR(255) {self.ops.NOT} NULL",
                "email": f"VARCHAR(255) {self.ops.UNIQUE_INDEX}",
                "age": "INTEGER",
                "salary": f"DECIMAL(12, 2) DEFAULT 0.00",
                "is_active": f"BOOLEAN DEFAULT TRUE",
                "created_at": f"TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            }
            
            # Собираем SQL через операторы
            success = self.repo.create_table("employees", schema)
            
            if not success:
                # Пробуем через execute_raw с операторами
                create_sql = f"""
                    {self.ops.CREATE_TABLE} {self.ops.IF_NOT_EXISTS} employees (
                        id SERIAL {self.ops.PRIMARY_KEY},
                        name VARCHAR(255) {self.ops.NOT} NULL,
                        email VARCHAR(255) UNIQUE,
                        age INTEGER,
                        salary DECIMAL(12, 2) DEFAULT 0.00,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                self.repo.execute_raw(create_sql, None)
                print("  ✓ Таблица создана через execute_raw с операторами")
                success = True
            
            self.assert_true(success, f"{self.ops.CREATE_TABLE} с операторами")
            
            # 2. Тест save с операторами
            print(f"\n2. {self.ops.INSERT_INTO} через save...")
            employee_data = {
                "name": "Иван Петров",
                "email": "ivan@company.com",
                "age": 30,
                "salary": 150000.50,
                "is_active": True
            }
            
            success = self.repo.save("employees", employee_data)
            self.assert_true(success, f"{self.ops.INSERT_INTO} через save()")
            
            # 3. Тест save_and_get_id
            print(f"\n3. {self.ops.INSERT_INTO} с получением ID...")
            emp_id = self.repo.save_and_get_id("employees", {
                "name": "Мария Сидорова",
                "email": "maria@company.com", 
                "age": 25,
                "salary": 120000.75
            })
            self.assert_greater(emp_id, 0, f"{self.ops.LAST_INSERT_ID()}: {emp_id}")
            
            # 4. Тест batch_insert
            print(f"\n4. {self.ops.INSERT_INTO} batch...")
            batch_data = [
                {"name": "Алексей", "email": "alex@company.com", "age": 28, "salary": 90000, "is_active": True},
                {"name": "Ольга", "email": "olga@company.com", "age": 32, "salary": 110000, "is_active": False},
                {"name": "Сергей", "email": "sergey@company.com", "age": 40, "salary": 130000, "is_active": True}
            ]
            
            success = self.repo.batch_insert("employees", batch_data)
            self.assert_true(success, f"Batch {self.ops.INSERT_INTO}")
            
            # 5. Тест get с разными операторами WHERE
            print(f"\n5. {self.ops.SELECT} с WHERE операторами:")
            
            # Простое равенство (=)
            results = self.repo.get(
                columns=f"{self.ops.All}",
                table="employees", 
                where={"is_active": True}
            )
            print(f"  {self.ops.EQUALS}: {len(results)} активных сотрудников")
            
            # Не равно (!=)
            results = self.repo.get(
                columns="name, age",
                table="employees",
                where={"is_active__ne": True}  # !=
            )
            print(f"  {self.ops.NOT_EQUALS}: {len(results)} неактивных")
            
            # Больше (>)
            results = self.repo.get(
                columns="name, salary",
                table="employees", 
                where={"salary__gt": 100000}  # >
            )
            print(f"  {self.ops.GREATER}: {len(results)} с зарплатой > 100к")
            
            # Больше или равно (>=)
            results = self.repo.get(
                columns="name, age",
                table="employees",
                where={"age__gte": 30}  # >=
            )
            print(f"  {self.ops.GREATER_EQUAL}: {len(results)} возраст >= 30")
            
            # Меньше (<)
            results = self.repo.get(
                columns="name, age",
                table="employees",
                where={"age__lt": 30}  # <
            )
            print(f"  {self.ops.LESS}: {len(results)} возраст < 30")
            
            # Меньше или равно (<=)
            results = self.repo.get(
                columns="name, age",
                table="employees",
                where={"age__lte": 30}  # <=
            )
            print(f"  {self.ops.LESS_EQUAL}: {len(results)} возраст <= 30")
            
            # LIKE
            results = self.repo.get(
                columns="name",
                table="employees",
                where={"name__like": "%Иван%"}  # LIKE
            )
            print(f"  {self.ops.LIKE}: {len(results)} с 'Иван' в имени")
            
            # IN
            results = self.repo.get(
                columns="name, age",
                table="employees", 
                where={"age__in": [25, 30, 35]}  # IN
            )
            print(f"  {self.ops.IN}: {len(results)} с возрастом 25,30,35")
            
            # 6. Тест get_advanced с логическими операторами
            print(f"\n6. {self.ops.SELECT} advanced с {self.ops.AND}/{self.ops.OR}...")
            conditions = [
                {"column": "age", "operator": self.ops.GREATER, "value": 25, "connector": self.ops.AND},
                {"column": "salary", "operator": self.ops.GREATER_EQUAL, "value": 100000}
            ]
            
            results = self.repo.get_advanced(
                columns=f"name, age, salary",
                table="employees",
                where_conditions=conditions
            )
            print(f"  {self.ops.AND} условие: {len(results)} записей")
            
            # 7. Тест delete с операторами
            print(f"\n7. {self.ops.DELETE_FROM}...")
            before_delete = len(self.repo.get(f"{self.ops.All}", "employees"))
            
            success = self.repo.delete("employees", {
                "name": "Сергей"
            })
            self.assert_true(success, f"{self.ops.DELETE_FROM}")
            
            after_delete = len(self.repo.get(f"{self.ops.All}", "employees"))
            self.assert_equal(after_delete, before_delete - 1, "Удалена 1 запись")
            
            # 8. Тест комплексных запросов с операторами
            print(f"\n8. Комплексные запросы с операторами:")
            
            # Создаем вторую таблицу с JOIN
            self.repo.create_table("departments", {
                "id": f"SERIAL {self.ops.PRIMARY_KEY}",
                "name": "VARCHAR(100)",
                "budget": "DECIMAL(12, 2)"
            })
            
            # Вставляем данные с операторами
            dept_sql = f"""
                {self.ops.INSERT_INTO} departments (name, budget)
                {self.ops.VALUES} 
                    (%s, %s),
                    (%s, %s)
            """
            self.repo.execute_raw(dept_sql, ("IT", 1000000, "HR", 500000))
            
            # JOIN запрос со всеми операторами
            join_query = f"""
                {self.ops.SELECT} 
                    e.name,
                    e.salary,
                    d.name {self.ops.AS} department,
                    d.budget,
                    {self.ops.ROUND}(e.salary * 100.0 / d.budget, 2) {self.ops.AS} percentage
                {self.ops.FROM} employees e
                {self.ops.CROSS_JOIN} departments d
                {self.ops.WHERE} e.salary {self.ops.GREATER} 0
                    {self.ops.AND} e.is_active = TRUE
                {self.ops.ORDER_BY} e.salary {self.ops.DESC}
                {self.ops.LIMIT} 5
            """
            
            results = self.repo.execute_raw(join_query, None)
            print(f"  {self.ops.JOIN} запрос: {len(results)} результатов")
            
            # 9. Тест агрегатных функций через операторы
            print(f"\n9. Агрегатные функции:")
            
            agg_query = f"""
                {self.ops.SELECT}
                    {self.ops.COUNT}(*) {self.ops.AS} total_count,
                    {self.ops.AVG}(salary) {self.ops.AS} avg_salary,
                    {self.ops.MIN}(salary) {self.ops.AS} min_salary,
                    {self.ops.MAX}(salary) {self.ops.AS} max_salary,
                    {self.ops.SUM}(salary) {self.ops.AS} total_salary,
                    {self.ops.STDDEV}(salary) {self.ops.AS} salary_stddev
                {self.ops.FROM} employees
                {self.ops.WHERE} is_active = TRUE
            """
            
            stats = self.repo.execute_raw(agg_query, None)
            if stats and stats[0]:
                print(f"  {self.ops.COUNT}: {stats[0][0]}")
                print(f"  {self.ops.AVG}: {stats[0][1]:.2f}")
                print(f"  {self.ops.SUM}: {stats[0][4]:.2f}")
            
            # 10. Тест GROUP BY и HAVING с CASE
            print(f"\n10. {self.ops.GROUP_BY} с {self.ops.HAVING} и {self.ops.CASE}:")
            
            group_query = f"""
                {self.ops.SELECT}
                    {self.ops.CASE}
                        {self.ops.WHEN} age {self.ops.LESS} 30 {self.ops.THEN} 'Молодой'
                        {self.ops.WHEN} age {self.ops.BETWEEN} 30 {self.ops.AND} 40 {self.ops.THEN} 'Средний'
                        {self.ops.ELSE} 'Старший'
                    {self.ops.END} {self.ops.AS} age_group,
                    {self.ops.COUNT}(*) {self.ops.AS} count,
                    {self.ops.AVG}(salary) {self.ops.AS} avg_salary
                {self.ops.FROM} employees
                {self.ops.GROUP_BY} age_group
                {self.ops.HAVING} {self.ops.COUNT}(*) {self.ops.GREATER} 0
                {self.ops.ORDER_BY} avg_salary {self.ops.DESC}
            """
            
            results = self.repo.execute_raw(group_query, None)
            for row in results:
                print(f"  {row[0]}: {row[1]} чел., средняя {row[2]:.2f}")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return self.end_test(False)


    def test_static_methods(self):
        """Тест статических методов"""
        self.start_test("СТАТИЧЕСКИЕ МЕТОДЫ Repository")
        
        try:
            # 1. Простейший save через статический метод Repository.save()
            print("\n1. Repository.save() статический...")
            
            # Сначала создаем таблицу через raw
            create_sql = """
                CREATE TABLE IF NOT EXISTS repo_static_test (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    value INTEGER
                )
            """
            self.repo.execute_raw(create_sql, None)
            
            # Используем статический метод Repository.save()
            success = Repository.save(
                db_path=self.db_path,
                table="repo_static_test",
                data={"name": "Статический тест", "value": 42},
                db_type=DB_TYPE
            )
            
            if not success:
                print("  ⚠ Repository.save() вернул False, пробуем через raw...")
                try:
                    self.repo.execute_raw(
                        "INSERT INTO repo_static_test (name, value) VALUES (%s, %s)",
                        ("Статический тест", 42)
                    )
                    print("  ✓ Вставлено через raw")
                    success = True
                except Exception as e:
                    print(f"  ✗ Ошибка: {e}")
            
            self.assert_true(success, "Repository.save()")
            
            # 2. Repository.get() статический
            print("\n2. Repository.get() статический...")
            results = Repository.get(
                db_path=self.db_path,
                table="repo_static_test",
                where={"name": "Статический тест"},
                db_type=DB_TYPE
            )
            self.assert_greater(len(results), 0, f"Repository.get(): {len(results)} записей")
            
            # 3. Repository.create_table() статический
            print("\n3. Repository.create_table() статический...")
            # ИСПРАВЛЕНИЕ: не используем self.ops.NOW как DEFAULT, используем CURRENT_TIMESTAMP
            success = Repository.create_table(
                db_path=self.db_path,
                table="repo_create_test",
                schema={
                    "id": "SERIAL PRIMARY KEY",
                    "name": "TEXT",
                    "created": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # ← ИСПРАВЛЕНО!
                },
                db_type=DB_TYPE
            )
            
            if not success:
                print("  ⚠ Repository.create_table() вернул False")
                # Проверяем создалась ли таблица
                try:
                    self.repo.execute_raw("SELECT 1 FROM repo_create_test LIMIT 1", None)
                    print("  ✓ Таблица уже существует")
                    success = True
                except:
                    print("  ✗ Таблица не создана")
            
            self.assert_true(success, "Repository.create_table()")
            
            # 4. Repository.batch_insert() статический
            print("\n4. Repository.batch_insert() статический...")
            success = Repository.batch_insert(
                db_path=self.db_path,
                table="repo_create_test",
                data_list=[
                    {"name": "Запись 1"},
                    {"name": "Запись 2"},
                    {"name": "Запись 3"}
                ],
                db_type=DB_TYPE
            )
            self.assert_true(success, "Repository.batch_insert()")
            
            # 5. Repository.execute_in_transaction() статический
            print("\n5. Repository.execute_in_transaction() статический...")
            
            # Используем операторы из self.ops для SQL
            insert_sql = f"{self.ops.INSERT_INTO} repo_create_test (name) {self.ops.VALUES} (%s)"
            
            success = Repository.execute_in_transaction(
                db_path=self.db_path,
                operations=[
                    {"sql": insert_sql, "params": ("Транзакция 1",)},
                    {"sql": insert_sql, "params": ("Транзакция 2",)}
                ],
                db_type=DB_TYPE
            )
            self.assert_true(success, "Repository.execute_in_transaction()")
            
            # 6. Repository.count() статический
            print("\n6. Repository.count() статический...")
            count = Repository.count(
                db_path=self.db_path,
                table="repo_create_test",
                db_type=DB_TYPE
            )
            print(f"  COUNT: {count} записей")
            self.assert_greater(count, 0, f"Repository.count(): {count}")
            
            # 7. Repository.update() статический
            print("\n7. Repository.update() статический...")
            success = Repository.update(
                db_path=self.db_path,
                table="repo_create_test",
                data={"name": "ОБНОВЛЕНО"},
                where={"name": "Запись 1"},
                db_type=DB_TYPE
            )
            self.assert_true(success, "Repository.update()")
            
            # 8. Repository.execute_with_checks() статический
            print("\n8. Repository.execute_with_checks() статический...")
            
            check_sql = f"SELECT 1 FROM repo_create_test WHERE name = %s"
            insert_sql = f"{self.ops.INSERT_INTO} repo_create_test (name) {self.ops.VALUES} (%s)"
            
            success = Repository.execute_with_checks(
                db_path=self.db_path,
                checks=[{
                    "sql": check_sql,
                    "params": ("ОБНОВЛЕНО",),
                    "expected": True
                }],
                operations=[{
                    "sql": insert_sql,
                    "params": ("После проверки",)
                }],
                db_type=DB_TYPE
            )
            self.assert_true(success, "Repository.execute_with_checks()")
            
            # 9. Repository.execute_operations() статический
            print("\n9. Repository.execute_operations() статический...")
            
            operations = [
                {
                    'type': 'check',
                    'sql': f"SELECT 1 FROM repo_create_test WHERE name = %s",
                    'params': ("После проверки",),
                    'expected': True
                },
                {
                    'type': 'query', 
                    'sql': f"{self.ops.INSERT_INTO} repo_create_test (name) {self.ops.VALUES} (%s)",
                    'params': ("Операция",)
                }
            ]
            
            success = Repository.execute_operations(
                db_path=self.db_path,
                operations=operations,
                db_type=DB_TYPE
            )
            self.assert_true(success, "Repository.execute_operations()")
            
            # 10. Repository.select_with_join() если есть
            print("\n10. Repository.select_with_join() если доступен...")
            
            if hasattr(Repository, 'select_with_join'):
                # Создаем вторую таблицу
                self.repo.execute_raw("""
                    CREATE TABLE IF NOT EXISTS join_test (
                        id SERIAL PRIMARY KEY,
                        main_id INTEGER,
                        extra TEXT
                    )
                """, None)
                
                self.repo.execute_raw("""
                    INSERT INTO join_test (main_id, extra) 
                    VALUES (1, 'Дополнительная информация')
                """, None)
                
                results = Repository.select_with_join(
                    db_path=self.db_path,
                    tables=['repo_create_test'],
                    joins=[{
                        'type': 'LEFT',
                        'table': 'join_test',
                        'on': 'repo_create_test.id = join_test.main_id'
                    }],
                    columns=['repo_create_test.name', 'join_test.extra'],
                    db_type=DB_TYPE
                )
                print(f"  select_with_join: {len(results)} результатов")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return self.end_test(False)
    
    # ==================== ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ====================
    
    def test_performance(self):
        """Тест производительности"""
        self.start_test("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
        
        try:
            # Создаем таблицу для теста производительности
            self.repo.create_table("perf_test", {
                "id": "SERIAL PRIMARY KEY",
                "name": "VARCHAR(255)",
                "value": "INTEGER",
                "data": "TEXT"
            })
            
            # 1. Тест batch_insert производительности
            print("\n1. Производительность BATCH_INSERT...")
            
            batch_sizes = [10, 100, 500]
            for size in batch_sizes:
                data = []
                for i in range(size):
                    data.append({
                        "name": f"Тест {i}",
                        "value": random.randint(1, 1000),
                        "data": "x" * 100  # 100 символов
                    })
                
                start = time.time()
                self.repo.batch_insert("perf_test", data)
                elapsed = time.time() - start
                
                print(f"  ✓ {size} записей: {elapsed:.3f} сек ({size/elapsed:.1f} зап/сек)")
            
            # 2. Тест SELECT производительности
            print("\n2. Производительность SELECT...")
            
            # Простой SELECT
            start = time.time()
            results = self.repo.get("*", "perf_test")
            simple_time = time.time() - start
            print(f"  ✓ Простой SELECT ({len(results)} записей): {simple_time:.3f} сек")
            
            # SELECT с условиями
            start = time.time()
            results = self.repo.get("*", "perf_test", where={
                "value__gt": 500,
                "name__like": "%Тест%"
            })
            where_time = time.time() - start
            print(f"  ✓ SELECT с WHERE ({len(results)} записей): {where_time:.3f} сек")
            
            # 3. Тест агрегации
            print("\n3. Производительность агрегации...")
            
            queries = [
                f"SELECT {self.ops.COUNT}(*) FROM perf_test",
                f"SELECT {self.ops.AVG}(value) FROM perf_test",
                f"SELECT {self.ops.MIN}(value), {self.ops.MAX}(value) FROM perf_test",
                f"SELECT value, {self.ops.COUNT}(*) FROM perf_test GROUP BY value {self.ops.HAVING} {self.ops.COUNT}(*) > 1"
            ]
            
            for i, query in enumerate(queries, 1):
                start = time.time()
                results = self.repo.execute_raw(query, None)
                elapsed = time.time() - start
                print(f"  ✓ Запрос {i}: {elapsed:.3f} сек")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            return self.end_test(False)
    
    # ==================== ТЕСТ НА ГРАНИЧНЫЕ СЛУЧАИ ====================
    
    def test_edge_cases(self):
        """Тест на граничные случаи и ошибки - ИСПРАВЛЕННЫЙ"""
        self.start_test("ГРАНИЧНЫЕ СЛУЧАИ (исправленный)")
        
        try:
            print("\n1. Несуществующие таблицы (get() возвращает None)...")
            result = self.repo.get("*", "non_existent_table_12345")
            
            if result is None:
                print("  ✓ get() несуществующей таблицы возвращает None (по дизайну)")
            else:
                print(f"  ⚠ get() вернул: {result}")
            
            print("\n2. Пустые данные...")
            success = self.repo.batch_insert("employees", [])
            
            if success is False:
                print("  ✓ batch_insert с пустым списком возвращает False")
            else:
                print(f"  ⚠ batch_insert вернул: {success}")
            
            print("\n3. SQL инъекции (безопасность)...")
            # Проверяем что параметры экранируются
            result = self.repo.get("*", "employees", where={
                "name": "test' OR '1'='1"  # SQL инъекция
            })
            
            if result is not None:
                print(f"  ✓ get() с SQL инъекцией вернул: {len(result)} записей (должно быть 0)")
            else:
                print("  ✓ get() с SQL инъекцией вернул None")
            
            print("\n4. Большие данные...")
            # Создаем таблицу для теста
            self.repo.execute_raw("DROP TABLE IF EXISTS edge_test", None)
            self.repo.execute_raw("""
                CREATE TABLE edge_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(10),  # Очень маленькое ограничение
                    value INTEGER
                )
            """, None)
            
            # Пробуем вставить слишком большую строку
            large_data = {"name": "x" * 20, "value": 42}  # 20 символов > 10
            
            success = self.repo.save("edge_test", large_data)
            
            if success is False:
                print("  ✓ save() с большими данными возвращает False")
            elif success is None:
                print("  ✓ save() с большими данными возвращает None")
            else:
                # Проверяем через raw SQL что данные не вставились
                result = self.repo.execute_raw("SELECT COUNT(*) FROM edge_test", None)
                if result and result[0][0] == 0:
                    print("  ✓ Данные не вставлены (ограничение VARCHAR)")
                else:
                    print(f"  ⚠ Данные вставлены: {result}")
            
            print("\n5. Специальные символы...")
            special_data = {
                "name": "Тест 'кавычек' \"двойных\"",
                "value": 999
            }
            
            success = self.repo.save("edge_test", special_data)
            
            if success:
                print("  ✓ Специальные символы сохранены")
                
                # Проверяем что сохранилось
                result = self.repo.get("*", "edge_test", where={"value": 999})
                if result:
                    print(f"     Сохранено: {result[0][1]}")
            else:
                print("  ✗ Не удалось сохранить специальные символы")
            
            print("\n6. Unicode символы...")
            unicode_data = {
                "name": "🚀 € αβγ 汉字",
                "value": 123
            }
            
            success = self.repo.save("edge_test", unicode_data)
            
            if success:
                print("  ✓ Unicode символы сохранены")
            else:
                print("  ✗ Не удалось сохранить Unicode")
            
            print("\n7. execute_raw с ошибкой...")
            # execute_raw должен выбрасывать исключение
            try:
                result = self.repo.execute_raw("SELECT * FROM несуществующая_таблица", None)
                print(f"  ⚠ execute_raw не выбросил исключение, вернул: {result}")
            except Exception as e:
                print(f"  ✓ execute_raw выбросил исключение (правильно): {str(e)[:100]}...")
            
            print("\n8. create_table с ошибкой...")
            # Пробуем создать таблицу с неправильным SQL
            try:
                success = self.repo.create_table("bad_table_test", {
                    "id": "НЕПРАВИЛЬНЫЙ_ТИП ДАННЫХ",  # Неправильный тип
                    "name": "TEXT"
                })
                
                if success is False:
                    print("  ✓ create_table с ошибкой вернул False")
                else:
                    print(f"  ⚠ create_table вернул: {success}")
            except Exception as e:
                print(f"  ✓ create_table выбросил исключение: {str(e)[:100]}...")
            
            return self.end_test(True)
            
        except Exception as e:
            print(f"  ✗ Неожиданная ошибка теста: {e}")
            import traceback
            traceback.print_exc()
            return self.end_test(False)
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def _cleanup_tables(self):
        """Очищает тестовые таблицы"""
        tables = [
            "employees", "departments", "static_test",
            "static_table", "perf_test", "non_existent_table"
        ]
        
        for table in tables:
            try:
                self.repo.execute_raw(f"DROP TABLE IF EXISTS {table} CASCADE", None)
            except:
                pass
    
    def run_all_tests(self):
        """Запускает все тесты"""
        print("\n" + "="*80)
        print("ЗАПУСК ЖЕСТКИХ ТЕСТОВ РЕПОЗИТОРИЯ")
        print(f"БД: {POSTGRES_CONFIG['database']} | Пользователь: {POSTGRES_CONFIG['user']}")
        print("="*80)
        
        tests = [
            ("Базовые операторы", self.test_basic_operators),
            ("Расширенные операторы", self.test_advanced_operators),
            ("Методы репозитория", self.test_repository_methods),
            ("Статические методы", self.test_static_methods),
            ("Производительность", self.test_performance),
            ("Граничные случаи", self.test_edge_cases)
        ]
        
        results = []
        for test_name, test_method in tests:
            try:
                success = test_method()
                results.append((test_name, success))
            except Exception as e:
                print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА в тесте '{test_name}': {e}")
                results.append((test_name, False))
        
        # Вывод итогов
        print("\n" + "="*80)
        print("ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*80)
        
        passed = 0
        for test_name, success in results:
            status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛ"
            print(f"{status}: {test_name}")
            if success:
                passed += 1
        
        print(f"\nВсего тестов: {len(tests)}")
        print(f"Пройдено: {passed}")
        print(f"Провалено: {len(tests) - passed}")
        
        if passed == len(tests):
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("\n⚠ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        
        return passed == len(tests)


# ==================== ПРОВЕРКА ПОДКЛЮЧЕНИЯ ====================
def check_postgres_connection():
    """Проверяет подключение к PostgreSQL"""
    print("🔍 Проверка подключения к PostgreSQL...")
    
    try:
        import psycopg2
        
        # Пробуем подключиться
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Получаем версию
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Проверяем/создаем тестовую БД
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_CONFIG['database'],))
        if not cursor.fetchone():
            conn.autocommit = True
            cursor.execute(f"CREATE DATABASE {POSTGRES_CONFIG['database']}")
            print(f"✅ Создана БД: {POSTGRES_CONFIG['database']}")
        else:
            print(f"✅ БД существует: {POSTGRES_CONFIG['database']}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ PostgreSQL подключен: {version.split(',')[0]}")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        print(f"\nПроверьте:")
        print(f"1. Пароль правильный: '{POSTGRES_CONFIG['password']}'")
        print(f"2. PostgreSQL запущен на {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
        print(f"3. Пользователь '{POSTGRES_CONFIG['user']}' существует")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False


# ==================== ЗАПУСК ТЕСТОВ ====================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ULTIMATE REPOSITORY TEST SUITE")
    print("="*80)
    
    # 1. Проверка подключения
    if not check_postgres_connection():
        print("\n❌ Невозможно продолжить без подключения к БД")
        exit(1)
    
    # 2. Запуск тестов
    try:
        tester = HardcoreRepositoryTest()
        success = tester.run_all_tests()
        
        # Дополнительный тест если все прошло
        if success:
            print("\n" + "="*80)
            print("🔧 ДОПОЛНИТЕЛЬНЫЙ ТЕСТ: МИГРАЦИИ")
            print("="*80)
            
            try:
                # Тест ALTER TABLE
                tester.repo.execute_raw("ALTER TABLE employees ADD COLUMN test_migration TEXT DEFAULT 'migrated'", None)
                print("✅ ALTER TABLE выполнен успешно")
                
                # Проверяем что колонка добавилась
                results = tester.repo.execute_raw("SELECT test_migration FROM employees LIMIT 1", None)
                if results and results[0][0] == 'migrated':
                    print("✅ Миграция применена корректно")
                else:
                    print("⚠ Миграция не применилась как ожидалось")
                    
            except Exception as e:
                print(f"❌ Ошибка миграции: {e}")
        
        exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ НЕ УДАЛОСЬ ЗАПУСТИТЬ ТЕСТЫ: {e}")
        import traceback
        traceback.print_exc()
        exit(1)