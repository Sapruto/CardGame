import json
from typing import List, Union, Optional, Tuple
from logging import getLogger

from src.base.orm.mainBD import BearSQL, DataTypes, Operators
from src.base.Config import *

logger = getLogger(__name__)

class InitTables:
    def __init__(self, db_path: dict = Constants.db_path, bd: BearSQL = None):
        self.db_path = db_path
        self.bd = bd or BearSQL(db_path)

    def initialize_tables(self):
        schemas = {
            MetricDefinition.TABLE: {
                MetricDefinition.ID: DataTypes.ID,
                MetricDefinition.METRIC_NAME: DataTypes.STRING,
                MetricDefinition.DESCRIPTION: DataTypes.STRING,
                MetricDefinition.DEFAULT_VALUE: DataTypes.INT
            },

            GameCharacter.TABLE: {
                GameCharacter.ID: DataTypes.ID,
                GameCharacter.NAME: f"{DataTypes.STRING} UNIQUE",
                GameCharacter.STATS: DataTypes.JSON,
                GameCharacter.CREATED_AT: DataTypes.DATETIME,
                GameCharacter.IMAGE_PATH: DataTypes.STRING
            },

            GameCard.TABLE: {
                GameCard.ID: DataTypes.ID,
                GameCard.CARD_UUID: DataTypes.STRING,
                GameCard.CARD_TEXT: DataTypes.STRING,
                GameCard.IMAGE_PATH: DataTypes.STRING
            },

            GameAnswer.TABLE: {
                GameAnswer.ID: DataTypes.ID,
                GameAnswer.CARD_UUID: DataTypes.STRING,
                GameAnswer.ANSWER_TEXT: DataTypes.STRING,
                GameAnswer.STATS_CHANGE: DataTypes.JSON,
                GameAnswer.ORDER_INDEX: DataTypes.INT
            },

            Resources.TABLE: {
                Resources.ID: DataTypes.ID,
                Resources.BG_PATH: DataTypes.STRING
            },

            Epilogs.TABLE: {
                Epilogs.ID: DataTypes.ID,
                Epilogs.TEXT: DataTypes.STRING,
                Epilogs.STATS_TO_RUN: DataTypes.JSON
            }
        }

        for table, schema in schemas.items():
            success = self.bd.create_table(table, schema)
