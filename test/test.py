import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base.Config import Constants
from src.base.orm.InternalBD import GeneralMethods


def drop_all_tables():
    print("УДАЛЕНИЕ ВСЕХ ТАБЛИЦ ИЗ БАЗЫ ДАННЫХ")

    tables = [
        'game_characters',
        'metrics_definition',
        'game_cards',
        'game_answers',
        'resources'
    ]

    try:
        with GeneralMethods(Constants.db_path) as gm:
            for table in tables:
                try:
                    gm.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"Таблица {table} удалена")
                except Exception as e:
                    print(f"Не удалось удалить {table}: {e}")

            gm.commit()
            print("\nВсе таблицы удалены!")

    except Exception as e:
        print(f"Ошибка: {e}")