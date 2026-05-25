import os
from dotenv import load_dotenv
from pathlib import Path
import json
from typing import Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel
from src.base.orm.mainBD import BearSQL, Operators
from src.base.Config import *
from src.api.requests.admin_requests import CharacterResponse, AnswerResponse, CardResponse
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import shutil
from fastapi import UploadFile

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TOKEN_KEY = os.getenv("TOKEN_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.password = os.getenv("ADMIN_PASSWORD")
        self.secret_key = TOKEN_KEY
        self.algorithm = ALGORITHM

    def verify_password(self, password: str) -> bool:
        if not self.password or not password:
            return False
        return self.password == password

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

class MetricService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.table = MetricDefinition.TABLE

    def add_metric(self, metric_name: str, description: str = "", default_value: float = 0.0) -> int:
        data = {
            MetricDefinition.METRIC_NAME: metric_name,
            MetricDefinition.DESCRIPTION: description,
            MetricDefinition.DEFAULT_VALUE: default_value
        }
        return self.db.save_and_get_id(self.table, data)

    def change_metric(self, metric_id: int, **kwargs) -> bool:
        where = {MetricDefinition.ID: metric_id}
        existing = self.db.get(columns=MetricDefinition.ID, table=self.table, where=where, fetch_one=True)
        if not existing:
            return False
        return self.db.advanced_update(self.table, kwargs, [{'column': MetricDefinition.ID, 'value': metric_id}])

    def delete_metric(self, metric_id: int) -> bool:
        where = {MetricDefinition.ID: metric_id}
        return self.db.delete(self.table, where)

    def get_metrics(self) -> List[Dict]:
        result = self.db.get(
            columns=f"{MetricDefinition.ID}, {MetricDefinition.METRIC_NAME}, {MetricDefinition.DESCRIPTION}, {MetricDefinition.DEFAULT_VALUE}",
            table=self.table,
            fetch_one=False
        )
        if not result:
            return []
        metrics = []
        for row in result:
            metrics.append({
                'id': row[0],
                'metric_name': row[1],
                'description': row[2],
                'default_value': row[3]
            })
        return metrics

class CharacterService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.table = GameCharacter.TABLE

    def add_character(self, name: str, stats: Dict, image_path: str = "") -> int:
        data = {
            GameCharacter.NAME: name,
            GameCharacter.STATS: json.dumps(stats),
            GameCharacter.IMAGE_PATH: image_path
        }
        return self.db.save_and_get_id(self.table, data)

    def change_character(self, character_id: int, **kwargs) -> bool:
        if 'stats' in kwargs:
            kwargs['stats'] = json.dumps(kwargs['stats'])
        where = {GameCharacter.ID: character_id}
        existing = self.db.get(columns=GameCharacter.ID, table=self.table, where=where, fetch_one=True)
        if not existing:
            return False
        return self.db.advanced_update(self.table, kwargs, [{'column': GameCharacter.ID, 'value': character_id}])

    def delete_character(self, character_id: int) -> bool:
        where = {GameCharacter.ID: character_id}
        return self.db.delete(self.table, where)

    def get_characters(self) -> List[CharacterResponse]:
        result = self.db.get(
            columns=f"{GameCharacter.ID}, {GameCharacter.NAME}, {GameCharacter.STATS}, {GameCharacter.IMAGE_PATH}",
            table=self.table,
            fetch_one=False
        )
        if not result:
            return []
        characters = []
        for row in result:
            characters.append(CharacterResponse(
                id=row[0],
                name=row[1],
                stats=json.loads(row[2]) if row[2] else {},
                image_path=row[3] or ""
            ))
        return characters

    def get_character(self, character_id: int) -> Optional[CharacterResponse]:
        where = {GameCharacter.ID: character_id}
        result = self.db.get(
            columns=f"{GameCharacter.ID}, {GameCharacter.NAME}, {GameCharacter.STATS}, {GameCharacter.IMAGE_PATH}",
            table=self.table,
            where=where,
            fetch_one=True
        )
        if not result:
            return None
        return CharacterResponse(
            id=result[0],
            name=result[1],
            stats=json.loads(result[2]) if result[2] else {},
            image_path=result[3] or ""
        )

class CardService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.table = GameCard.TABLE

    def add_card(self, card_text: str, image_path: str = "") -> int:
        card_uuid = str(uuid4())
        data = {
            GameCard.CARD_UUID: card_uuid,
            GameCard.CARD_TEXT: card_text,
            GameCard.IMAGE_PATH: image_path
        }
        return self.db.save_and_get_id(self.table, data)

    def change_card(self, card_id: int, **kwargs) -> bool:
        where = {GameCard.ID: card_id}
        existing = self.db.get(columns=GameCard.ID, table=self.table, where=where, fetch_one=True)
        if not existing:
            return False
        return self.db.advanced_update(self.table, kwargs, [{'column': GameCard.ID, 'value': card_id}])

    def delete_card(self, card_id: int) -> bool:
        where = {GameCard.ID: card_id}
        return self.db.delete(self.table, where)

    def get_cards(self) -> List[CardResponse]:
        result = self.db.get(
            columns=f"{GameCard.ID}, {GameCard.CARD_UUID}, {GameCard.CARD_TEXT}, {GameCard.IMAGE_PATH}",
            table=self.table,
            fetch_one=False
        )
        if not result:
            return []
        cards = []
        for row in result:
            cards.append(CardResponse(
                id=row[0],
                card_uuid=row[1],
                card_text=row[2],
                image_path=row[3] or ""
            ))
        return cards

    def get_card(self, card_id: int) -> Optional[CardResponse]:
        where = {GameCard.ID: card_id}
        result = self.db.get(
            columns=f"{GameCard.ID}, {GameCard.CARD_UUID}, {GameCard.CARD_TEXT}, {GameCard.IMAGE_PATH}",
            table=self.table,
            where=where,
            fetch_one=True
        )
        if not result:
            return None
        return CardResponse(
            id=result[0],
            card_uuid=result[1],
            card_text=result[2],
            image_path=result[3] or ""
        )

    def get_card_by_uuid(self, card_uuid: str) -> Optional[CardResponse]:
        where = {GameCard.CARD_UUID: card_uuid}
        result = self.db.get(
            columns=f"{GameCard.ID}, {GameCard.CARD_UUID}, {GameCard.CARD_TEXT}, {GameCard.IMAGE_PATH}",
            table=self.table,
            where=where,
            fetch_one=True
        )
        if not result:
            return None
        return CardResponse(
            id=result[0],
            card_uuid=result[1],
            card_text=result[2],
            image_path=result[3] or ""
        )

class AnswerService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.table = GameAnswer.TABLE

    def add_answer(self, card_uuid: str, answer_text: str, stats_change: Dict, order_index: int) -> int:
        data = {
            GameAnswer.CARD_UUID: card_uuid,
            GameAnswer.ANSWER_TEXT: answer_text,
            GameAnswer.STATS_CHANGE: json.dumps(stats_change),
            GameAnswer.ORDER_INDEX: order_index
        }
        return self.db.save_and_get_id(self.table, data)

    def change_answer(self, answer_id: int, **kwargs) -> bool:
        if 'stats_change' in kwargs:
            kwargs['stats_change'] = json.dumps(kwargs['stats_change'])
        where = {GameAnswer.ID: answer_id}
        existing = self.db.get(columns=GameAnswer.ID, table=self.table, where=where, fetch_one=True)
        if not existing:
            return False
        return self.db.advanced_update(self.table, kwargs, [{'column': GameAnswer.ID, 'value': answer_id}])

    def delete_answer(self, answer_id: int) -> bool:
        where = {GameAnswer.ID: answer_id}
        return self.db.delete(self.table, where)

    def get_answers_to_card(self, card_uuid: str) -> List[AnswerResponse]:
        where = {GameAnswer.CARD_UUID: card_uuid}
        result = self.db.get(
            columns=f"{GameAnswer.ID}, {GameAnswer.CARD_UUID}, {GameAnswer.ANSWER_TEXT}, {GameAnswer.STATS_CHANGE}, {GameAnswer.ORDER_INDEX}",
            table=self.table,
            where=where,
            fetch_one=False
        )
        if not result:
            return []
        answers = []
        for row in result:
            answers.append(AnswerResponse(
                id=row[0],
                card_uuid=row[1],
                answer_text=row[2],
                stats_change=json.loads(row[3]) if row[3] else {},
                order_index=row[4] if row[4] is not None else 0
            ))
        answers.sort(key=lambda x: x.order_index)
        return answers

    def get_answer(self, answer_id: int) -> Optional[AnswerResponse]:
        where = {GameAnswer.ID: answer_id}
        result = self.db.get(
            columns=f"{GameAnswer.ID}, {GameAnswer.CARD_UUID}, {GameAnswer.ANSWER_TEXT}, {GameAnswer.STATS_CHANGE}, {GameAnswer.ORDER_INDEX}",
            table=self.table,
            where=where,
            fetch_one=True
        )
        if not result:
            return None
        return AnswerResponse(
            id=result[0],
            card_uuid=result[1],
            answer_text=result[2],
            stats_change=json.loads(result[3]) if result[3] else {},
            order_index=result[4]
        )

class ImageService:
    def __init__(self):
        self.db = BearSQL(Constants.db_path)
        self.table = Resources.TABLE
        self.upload_dir = str(Path(__file__).parent.parent.parent / "static" / "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def add_image(self, file: UploadFile, folder: str) -> Optional[str]:
        ext = file.filename.split('.')[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = f"{self.upload_dir}/{folder}/{filename}"
        os.makedirs(f"{self.upload_dir}/{folder}", exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        db_path = f"/static/uploads/{folder}/{filename}"
        data = {Resources.BG_PATH: db_path}
        self.db.save(self.table, data)
        return db_path

    def change_image(self, image_id: int, new_file: UploadFile) -> bool:
        existing = self.db.get(columns=Resources.BG_PATH, table=self.table, where={Resources.ID: image_id}, fetch_one=True)
        if not existing:
            return False
        old_path = existing[0]
        if old_path and os.path.exists(old_path):
            os.remove(old_path)
        ext = new_file.filename.split('.')[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = f"static/uploads/{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(new_file.file, buffer)
        new_db_path = f"/static/uploads/{filename}"
        self.db.advanced_update(self.table, {Resources.BG_PATH: new_db_path}, [{'column': Resources.ID, 'value': image_id}])
        return True

    def delete_image(self, image_id: int) -> bool:
        existing = self.db.get(columns=Resources.BG_PATH, table=self.table, where={Resources.ID: image_id}, fetch_one=True)
        if not existing:
            return False
        file_path = existing[0]
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        where = {Resources.ID: image_id}
        return self.db.delete(self.table, where)

    def get_images_paths(self) -> List[str]:
        result = self.db.get(columns=Resources.BG_PATH, table=self.table, fetch_one=False)
        if not result:
            return []
        return [row[0] for row in result]

    def get_images(self) -> List[Dict]:
        result = self.db.get(columns=f"{Resources.ID}, {Resources.BG_PATH}", table=self.table, fetch_one=False)
        if not result:
            return []
        return [{"id": row[0], "path": row[1]} for row in result]

    def get_files_in_folder(self, folder: str) -> List[str]:
        folder_path = f"{self.upload_dir}/{folder}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            return []
        files = [f for f in os.listdir(folder_path) if os.path.isfile(f"{folder_path}/{f}")]
        return files

    def get_bg(self) -> str:
        result = self.db.get(columns=Resources.BG_PATH, table=self.table, fetch_one=True)
        if result and len(result) > 0:
            return result[0]
        return ""

    def set_bg(self, bg_path: str) -> bool:
        existing = self.db.get(columns=Resources.ID, table=self.table, fetch_one=True)
        if existing:
            return self.db.advanced_update(self.table, {Resources.BG_PATH: bg_path}, [{'column': Resources.ID, 'value': existing[0]}])
        else:
            return self.db.save(self.table, {Resources.BG_PATH: bg_path})

def get_admin_service():
    return AdminService()

def get_metric_service():
    return MetricService()

def get_character_service():
    return CharacterService()

def get_card_service():
    return CardService()

def get_answer_service():
    return AnswerService()

def get_image_service():
    return ImageService()