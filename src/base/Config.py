import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Constants:
    db_path = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": os.getenv("DB_NAME", "testdb"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "")
    }

class MetricDefinition:
    TABLE = "metrics_definition"

    ID = "id"
    METRIC_NAME = "metric_name"
    DESCRIPTION = "description"
    DEFAULT_VALUE = "default_value"


class GameCharacter:
    TABLE = "game_characters"

    ID = "id"
    NAME = "name"
    STATS = "stats"
    CREATED_AT = "created_at"

    IMAGE_PATH = "image_path"


class GameCard:
    TABLE = "game_cards"

    ID = "id"
    CARD_UUID = "card_uuid"
    CARD_TEXT = "card_text"

    IMAGE_PATH = "image_path"

class GameAnswer:
    TABLE = "game_answers"

    ID = "id"
    CARD_UUID = "card_uuid"
    ANSWER_TEXT = "answer_text"
    STATS_CHANGE = "stats_change"
    ORDER_INDEX = "order_index"

class Resources:
    TABLE = "resources"

    ID = "id"
    BG_PATH = "bg_path"
