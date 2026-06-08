from fastapi import APIRouter, Form, HTTPException, status, Depends, Cookie, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import AsyncSessionLocal
from src.db.managers.metric_manager import get_metric_manager
from src.db.managers.character_manager import get_character_manager
from src.db.managers.question_manager import get_question_manager
from src.db.managers.answer_manager import get_answer_manager
from src.db.managers.epilogue_manager import get_epilogue_manager
from src.db.managers.resource_manager import get_resource_manager
from src.services.admin_service import ImageService, get_image_service, AdminAuthService, get_admin_auth_service
from src.models.shemas.admin_dto import *
import uuid

admin_router = APIRouter(tags=["admin"])

def verify_admin_token(admin_token: str = Cookie(None)):
    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token in cookie"
        )
    auth_service = get_admin_auth_service()
    payload = auth_service.verify_token(admin_token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload

@admin_router.post("/api/admin_login")
async def admin_login(password: str = Form(...)):
    auth_service = get_admin_auth_service()
    is_verify = auth_service.verify_password(password)
    if not is_verify:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid password"}
        )
    token_data = {"sub": "admin", "role": "admin"}
    token = auth_service.create_access_token(token_data)
    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800,
        path="/"
    )
    return response

@admin_router.post("/api/admin_exit", dependencies=[Depends(verify_admin_token)])
async def admin_exit():
    response = JSONResponse(content={"success": True})
    response.delete_cookie("admin_token")
    return response


@admin_router.get("/api/metrics", response_model=List[MetricResponseSchema], dependencies=[Depends(verify_admin_token)])
async def get_metrics():
    async with AsyncSessionLocal() as session:
        manager = get_metric_manager()
        metrics = await manager.get_all(session)
        return [MetricResponseSchema(id=m.id, metric_name=m.metric_name, description=m.description, value=m.default_value) for m in metrics]

@admin_router.post("/api/metrics", dependencies=[Depends(verify_admin_token)])
async def create_metric(data: MetricCreateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_metric_manager()

        if await manager.exists(session, metric_name=data.metric_name):
            raise HTTPException(400, f"Metric {data.metric_name} already exists")

        metric = await manager.create(
            session,
            metric_name=data.metric_name,
            description=data.description,
            default_value=data.default_value
        )
        await session.commit()
        return {"id": metric.id, "message": "Metric created"}

@admin_router.put("/api/metrics/{metric_id}", dependencies=[Depends(verify_admin_token)])
async def update_metric(metric_id: int, data: MetricUpdateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_metric_manager()
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(400, "No data to update")

        await manager.update(session, metric_id, **update_data)
        await session.commit()
        return {"message": "Metric updated"}

@admin_router.delete("/api/metrics/{metric_id}", dependencies=[Depends(verify_admin_token)])
async def delete_metric(metric_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_metric_manager()
        await manager.delete(session, metric_id)
        await session.commit()
        return {"message": "Metric deleted"}


@admin_router.get("/api/characters", response_model=List[CharacterResponseSchema], dependencies=[Depends(verify_admin_token)])
async def get_characters():
    async with AsyncSessionLocal() as session:
        manager = get_character_manager()
        characters = await manager.get_all(session)
        result = []
        for c in characters:
            stats = c.stats if isinstance(c.stats, list) else json.loads(c.stats) if c.stats else []
            result.append(CharacterResponseSchema(
                id=c.id,
                name=c.name,
                stats=stats,
                image_path=c.image_path or ""
            ))
        return result

@admin_router.get("/api/characters/{character_id}", response_model=CharacterResponseSchema, dependencies=[Depends(verify_admin_token)])
async def get_character(character_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_character_manager()
        character = await manager.get_by_id(session, character_id)
        if not character:
            raise HTTPException(404, "Character not found")
        stats = character.stats if isinstance(character.stats, list) else json.loads(character.stats) if character.stats else []
        return CharacterResponseSchema(
            id=character.id,
            name=character.name,
            stats=stats,
            image_path=character.image_path or ""
        )

@admin_router.post("/api/characters", dependencies=[Depends(verify_admin_token)])
async def create_character(data: CharacterCreateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_character_manager()
        metric_manager = get_metric_manager()

        if data.stats is None:
            metrics = await metric_manager.get_all(session)
            stats = [
                {
                    "id": m.id,
                    "name": m.metric_name,
                    "description": m.description,
                    "value": m.default_value
                }
                for m in metrics
            ]
        else:
            stats = []
            for stat_name, stat_value in data.stats.items():
                metric = await metric_manager.get_by_field(session, stat_name, "metric_name")
                stats.append({
                    "id": metric.id if metric else None,
                    "name": stat_name,
                    "description": metric.description if metric else "",
                    "value": stat_value
                })

        character = await manager.create(
            session,
            name=data.name,
            stats=stats,
            image_path=data.image_path or ""
        )
        await session.commit()
        return {"id": character.id, "message": "Character created"}

@admin_router.put("/api/characters/{character_id}", dependencies=[Depends(verify_admin_token)])
async def update_character(character_id: int, data: CharacterUpdateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_character_manager()
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(400, "No data to update")

        await manager.update(session, character_id, **update_data)
        await session.commit()
        return {"message": "Character updated"}

@admin_router.delete("/api/characters/{character_id}", dependencies=[Depends(verify_admin_token)])
async def delete_character(character_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_character_manager()
        await manager.delete(session, character_id)
        await session.commit()
        return {"message": "Character deleted"}


@admin_router.get("/api/cards", response_model=List[CardResponseSchema], dependencies=[Depends(verify_admin_token)])
async def get_cards():
    async with AsyncSessionLocal() as session:
        manager = get_question_manager()
        questions = await manager.get_all(session)
        return [CardResponseSchema(id=q.id, card_uuid=q.question_uuid, card_text=q.question_text, image_path=q.image_path or "", next_question_uuid=q.next_question_uuid, is_first=q.is_first) for q in questions]

@admin_router.get("/api/cards/{question_id}", response_model=CardResponseSchema, dependencies=[Depends(verify_admin_token)])
async def get_card(question_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_question_manager()
        question = await manager.get_by_id(session, question_id)
        if not question:
            raise HTTPException(404, "Question not found")
        return CardResponseSchema(id=question.id, card_uuid=question.question_uuid, card_text=question.question_text, image_path=question.image_path or "", next_question_uuid=question.next_question_uuid, is_first=question.is_first)


@admin_router.post("/api/cards", dependencies=[Depends(verify_admin_token)])
async def create_card(data: CardCreateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_question_manager()

        question = await manager.create(
            session,
            question_uuid=str(uuid.uuid4()),
            question_text=data.card_text,
            image_path=data.image_path or "",
            next_question_uuid=data.next_question_uuid or None,
            is_first=data.is_first or False
        )
        await session.commit()
        return {"id": question.id, "message": "Card created"}

@admin_router.put("/api/cards/{question_id}", dependencies=[Depends(verify_admin_token)])
async def update_card(question_id: int, data: CardUpdateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_question_manager()
        update_data = data.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(400, "No data to update")

        if 'card_text' in update_data:
            update_data['question_text'] = update_data.pop('card_text')

        if update_data.get('is_first'):
            card = await manager.get_by_id(session, question_id)
            if card:
                await manager.set_as_first(session, card.question_uuid)
            update_data.pop('is_first', None)

        if update_data:
            await manager.update(session, question_id, **update_data)

        await session.commit()
        return {"message": "Card updated"}

@admin_router.delete("/api/cards/{question_id}", dependencies=[Depends(verify_admin_token)])
async def delete_card(question_id: int):
    async with AsyncSessionLocal() as session:
        question_manager = get_question_manager()
        answer_manager = get_answer_manager()

        question = await question_manager.get_by_id(session, question_id)
        if question:
            answers = await answer_manager.get_by_question(session, question.question_uuid)
            for answer in answers:
                await answer_manager.delete(session, answer.id)

        await question_manager.delete(session, question_id)
        await session.commit()
        return {"message": "Card deleted"}


@admin_router.get("/api/answers", response_model=List[AnswerResponseSchema], dependencies=[Depends(verify_admin_token)])
async def get_answers(card_uuid: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        manager = get_answer_manager()
        if card_uuid:
            answers = await manager.get_by_question(session, card_uuid)
        else:
            answers = await manager.get_all(session)
        result = []
        for a in answers:
            stats_change = a.stats_change if isinstance(a.stats_change, list) else json.loads(a.stats_change) if a.stats_change else []
            result.append(AnswerResponseSchema(
                id=a.id,
                card_uuid=a.question_uuid,
                answer_text=a.answer_text,
                stats_change=stats_change,
                order_index=a.order_index
            ))
        return result

@admin_router.get("/api/answers/{answer_id}", response_model=AnswerResponseSchema, dependencies=[Depends(verify_admin_token)])
async def get_answer(answer_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_answer_manager()
        answer = await manager.get_by_id(session, answer_id)
        if not answer:
            raise HTTPException(404, "Answer not found")
        stats_change = answer.stats_change if isinstance(answer.stats_change, list) else json.loads(answer.stats_change) if answer.stats_change else []
        return AnswerResponseSchema(
            id=answer.id,
            card_uuid=answer.question_uuid,
            answer_text=answer.answer_text,
            stats_change=stats_change,
            order_index=answer.order_index
        )

@admin_router.post("/api/answers", dependencies=[Depends(verify_admin_token)])
async def create_answer(data: AnswerCreateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_answer_manager()
        answer = await manager.create(
            session,
            question_uuid=data.card_uuid,
            answer_text=data.answer_text,
            stats_change=[sc.dict() for sc in data.stats_change],
            order_index=data.order_index
        )
        await session.commit()
        return {"id": answer.id, "message": "Answer created"}

@admin_router.put("/api/answers/{answer_id}", dependencies=[Depends(verify_admin_token)])
async def update_answer(answer_id: int, data: AnswerUpdateSchema):
    async with AsyncSessionLocal() as session:
        manager = get_answer_manager()
        update_data = data.model_dump(exclude_none=True)
        if "stats_change" in update_data and update_data["stats_change"] is not None:
            update_data["stats_change"] = [sc.dict() for sc in update_data["stats_change"]]

        if not update_data:
            raise HTTPException(400, "No data to update")

        await manager.update(session, answer_id, **update_data)
        await session.commit()
        return {"message": "Answer updated"}

@admin_router.delete("/api/answers/{answer_id}", dependencies=[Depends(verify_admin_token)])
async def delete_answer(answer_id: int):
    async with AsyncSessionLocal() as session:
        manager = get_answer_manager()
        await manager.delete(session, answer_id)
        await session.commit()
        return {"message": "Answer deleted"}


@admin_router.post("/api/upload_image", dependencies=[Depends(verify_admin_token)])
async def upload_image(folder: str = Form(...), file: UploadFile = File(...)):
    image_service = get_image_service()
    image_path = await image_service.add_image(file, folder)
    if not image_path:
        raise HTTPException(status_code=500, detail="Failed to upload image")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"path": image_path, "message": "Image uploaded"})

@admin_router.get("/api/images/{folder}", dependencies=[Depends(verify_admin_token)])
async def get_images(folder: str):
    image_service = get_image_service()
    return await image_service.get_files_in_folder(folder)


@admin_router.get("/api/resources/bg", dependencies=[Depends(verify_admin_token)])
async def get_bg():
    async with AsyncSessionLocal() as session:
        manager = get_resource_manager()
        bg_path = await manager.get_bg(session)
        return {"bg_path": bg_path}

@admin_router.post("/api/resources/bg", dependencies=[Depends(verify_admin_token)])
async def set_bg(bg_path: str):
    async with AsyncSessionLocal() as session:
        manager = get_resource_manager()
        await manager.set_bg(session, bg_path)
        await session.commit()
        return {"success": True}