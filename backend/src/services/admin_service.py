from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import shutil
from pathlib import Path
import os
from dotenv import load_dotenv
from fastapi import UploadFile
from logging import getLogger

logger = getLogger(__name__)

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TOKEN_KEY = os.getenv("TOKEN_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminAuthService:
    def __init__(self):
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

class ImageService:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.media_dir = self.project_root / "media"
        self.upload_dir = self.media_dir / "uploads"

        self.media_dir.mkdir(exist_ok=True)
        self.upload_dir.mkdir(exist_ok=True)

    async def add_image(self, file: UploadFile, folder: str) -> Optional[str]:
        try:
            ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
            filename = f"{uuid4()}.{ext}"

            target_folder = self.upload_dir / folder
            target_folder.mkdir(parents=True, exist_ok=True)

            file_path = target_folder / filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            db_path = f"/media/uploads/{folder}/{filename}"

            return db_path

        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return None

    async def get_files_in_folder(self, folder: str) -> List[str]:
        folder_path = self.upload_dir / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            return []

        files = [f.name for f in folder_path.iterdir() if f.is_file()]
        return files

    async def delete_file(self, file_path: str) -> bool:
        try:
            full_path = self.project_root / file_path.lstrip('/')
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


def get_admin_auth_service() -> AdminAuthService:
    return AdminAuthService()

def get_image_service() -> ImageService:
    return ImageService()