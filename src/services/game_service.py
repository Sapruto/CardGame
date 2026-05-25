import json
from typing import List, Dict, Any
from dataclasses import dataclass
import logging
import random
from xml.dom.pulldom import CHARACTERS

from src.base.orm.mainBD import BearSQL, Operators
from src.base.Config import *

from src.api.requests.game_requests import *

logger = logging.getLogger(__name__)

@dataclass
class Question:
    uuid: str
    text: str
    answers: List[Dict[str, Any]]

@dataclass
class Character:
    id: int
    name: str
    stats: Dict[str, int]

class GameService:
    def __init__(self, db_path: dict = Constants.db_path, bd: BearSQL = None):
        self.db_path = db_path
        self.bd = bd or BearSQL(db_path)

        self.all_characters: List[Character] = []
        self.all_questions: List[Question] = []

        self.load_all()

    def _load_answers_to_question(self, question: Question = None):
        if not question:
            return

        raw_answers = self.bd.get(
            columns=f"{GameAnswer.ID}, {GameAnswer.CARD_UUID}, {GameAnswer.ANSWER_TEXT}, {GameAnswer.STATS_CHANGE}, {GameAnswer.ORDER_INDEX}",
            table=GameAnswer.TABLE,
            where={GameAnswer.CARD_UUID: question.uuid}
        )
        if not raw_answers:
            logger.warning("No answers found in database")
            return

        for raw_answer in raw_answers:
            stats_change = json.loads(raw_answer[3]) if raw_answer[3] else {}

            answer = {
                "text": raw_answer[2],
                "stats_change": stats_change
            }
            question.answers.append(answer)

    def _load_questions(self):
        raw_questions = self.bd.get(
            columns=f"{GameCard.ID}, {GameCard.CARD_UUID}, {GameCard.CARD_TEXT}",
            table=GameCard.TABLE)
        if not raw_questions:
            logger.warning("No questions found in database")
            return

        for raw_question in raw_questions:
            question = Question(
                uuid=raw_question[1],
                text=raw_question[2],
                answers=[]
            )
            self.all_questions.append(question)
            self._load_answers_to_question(question)

    def _load_characters(self):
        raw_characters = self.bd.get(
            columns=f"{GameCharacter.ID}, {GameCharacter.NAME}, {GameCharacter.STATS}",
            table=GameCharacter.TABLE
        )
        if not raw_characters:
            logger.warning("No characters found in database")
            return

        for raw_character in raw_characters:
            stats = json.loads(raw_character[2]) if raw_character[2] else {}

            character = Character(
                id=raw_character[0],
                name=raw_character[1],
                stats=stats
            )
            self.all_characters.append(character)

    def _get_all_metrics(self) -> List[Dict]:
        result = self.bd.get(
            columns=f"{MetricDefinition.ID}, {MetricDefinition.METRIC_NAME}, {MetricDefinition.DESCRIPTION}, {MetricDefinition.DEFAULT_VALUE}",
            table=MetricDefinition.TABLE
        )
        if not result:
            return []

        metrics = []
        for row in result:
            metrics.append({
                MetricDefinition.ID: row[0],
                MetricDefinition.METRIC_NAME: row[1],
                MetricDefinition.DESCRIPTION: row[2],
                MetricDefinition.DEFAULT_VALUE: row[3]
            })
        return metrics

    def load_all(self) -> None:
        self._load_questions()
        self._load_characters()
        logger.info(f"Loaded {len(self.all_questions)} questions and {len(self.all_characters)} characters")

    def get_new_game(self, max_rounds: int = 0) -> GameStartResponse:
        if not self.all_characters or not self.all_questions:
            return GameStartResponse(character={"id": 0, "name": "Ошибка", "stats": {}},
                questions=[],
                metrics=[])

        if max_rounds == 0:
            max_rounds = len(self.all_questions)

        character = random.choice(self.all_characters)

        shuffled_questions = random.sample(self.all_questions, len(self.all_questions))
        questions = shuffled_questions[:max_rounds]

        metrics = self._get_all_metrics()

        return GameStartResponse(character={
                "id": character.id,
                "name": character.name,
                "stats": character.stats
            },
            questions=[
                {
                    "uuid": q.uuid,
                    "text": q.text,
                    "answers": q.answers
                }
                for q in questions
            ],
            metrics=[
                {
                    "name": m[MetricDefinition.METRIC_NAME],
                    "description": m[MetricDefinition.DESCRIPTION]
                }
                for m in metrics
            ])

    def get_assets(self, request: GameAssetsRequest) -> GameAssetsResponse:
        character_result = self.bd.get(
            GameCharacter.IMAGE_PATH,
            GameCharacter.TABLE,
            {GameCharacter.NAME: request.character},
            fetch_one=True
        )
        character_path = character_result[0] if character_result and len(character_result) > 0 else ""
        if character_path:
            character_path = character_path.replace('/static/', '/media/')

        questions_paths = {}
        for question_uuid in request.questions:
            question_result = self.bd.get(
                GameCard.IMAGE_PATH,
                GameCard.TABLE,
                {GameCard.CARD_UUID: question_uuid},
                fetch_one=True
            )
            if question_result and len(question_result) > 0:
                path = question_result[0]
                if path:
                    path = path.replace('/static/', '/media/')
                questions_paths[question_uuid] = path

        bg_result = self.bd.get(Resources.BG_PATH, Resources.TABLE, fetch_one=True)
        bg_path = bg_result[0] if bg_result and len(bg_result) > 0 else ""
        if bg_path:
            bg_path = bg_path.replace('/static/', '/media/')

        return GameAssetsResponse(
            bg=bg_path,
            character_image=character_path,
            questions_images=questions_paths
        )

    def process_game_result(self, final_stats: Dict[str, int], character_id: int = None) -> GameResultResponse:
        best_match = self._find_closest_character(final_stats, character_id)

        if not best_match and character_id is not None:
            for char in self.all_characters:
                if char.id == character_id:
                    best_match = char
                    break

        if not best_match and self.all_characters:
            best_match = self.all_characters[0]

        if not best_match:
            return GameResultResponse(
                success=False,
                message="Не удалось определить похожего персонажа",
                matched_character={},
                your_stats=final_stats
            )

        return GameResultResponse(
            success=True,
            message=f"Поздравляем! Вы похожи на {best_match.name}",
            matched_character={
                "id": best_match.id,
                "name": best_match.name,
                "stats": best_match.stats
            },
            your_stats=final_stats
        )

    def _find_closest_character(self, stats: Dict[str, int], exclude_id: int = None) -> Character:
        if not self.all_characters:
            return None

        characters = [c for c in self.all_characters if c.id != exclude_id] if exclude_id else self.all_characters

        best_match = None
        min_difference = float('inf')

        for character in characters:
            difference = 0
            for metric, value in stats.items():
                char_value = character.stats.get(metric, 0)
                difference += abs(value - char_value)

            if difference < min_difference:
                min_difference = difference
                best_match = character

        return best_match