from fastapi import APIRouter, Form, HTTPException, status, Depends, Cookie, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional

from src.api.requests.admin_requests import (
    CharacterCreateRequest, CharacterUpdateRequest,
    CardCreateRequest, CardUpdateRequest, AnswerCreateRequest,
    AnswerUpdateRequest, MetricCreateRequest, MetricUpdateRequest
)
from src.services.admin_serviсe import *

admin_router = APIRouter(tags=["admin"])


def verify_admin_token(admin_token: str = Cookie(None)):
    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token in cookie"
        )

    admin_service = get_admin_service()
    payload = admin_service.verify_token(admin_token)

    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="BAD TOKEN"
        )
    return payload


@admin_router.post("/api/admin_login")
def admin_login(password: str = Form(...)):
    admin_service = get_admin_service()
    is_verify = admin_service.verify_password(password)

    if is_verify:
        token_data = {"sub": "admin", "role": "admin"}
        token = admin_service.create_access_token(data=token_data)
        if token:
            response = JSONResponse(content={"success": True})
            response.set_cookie(
                key="admin_token",
                value=token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=1800,
                path="/"
            )# FOR PRODUCTION YOU AND I NEED TO F*CK THIS CODE AND CHANGE THIS FOR TRUE
            return response
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "YOU ARE STUPED BLACK MONKEY"}
    )

@admin_router.post("/api/admin_exit", dependencies=[Depends(verify_admin_token)])
def admin_exit(admin_token: str = Cookie(None)):
    response = JSONResponse(content={"success": True})
    response.delete_cookie("admin_token")
    return response


@admin_router.post("/api/metrics", dependencies=[Depends(verify_admin_token)])
def create_metric(request: MetricCreateRequest) -> JSONResponse:
    service = get_metric_service()
    metric_id = service.add_metric(
        metric_name=request.metric_name,
        description=request.description,
        default_value=request.default_value
    )
    if metric_id > 0:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"id": metric_id, "message": "Metric created"}
        )
    raise HTTPException(status_code=500, detail="Failed to create metric")


@admin_router.put("/api/metrics/{metric_id}", dependencies=[Depends(verify_admin_token)])
def update_metric(metric_id: int, request: MetricUpdateRequest) -> JSONResponse:
    service = get_metric_service()
    update_data = request.dict(exclude_unset=True)
    if update_data:
        success = service.change_metric(metric_id, **update_data)
        if success:
            return JSONResponse(content={"message": "Metric updated"})
    raise HTTPException(status_code=404, detail="Metric not found")


@admin_router.delete("/api/metrics/{metric_id}", dependencies=[Depends(verify_admin_token)])
def delete_metric(metric_id: int) -> JSONResponse:
    service = get_metric_service()
    success = service.delete_metric(metric_id)
    if success:
        return JSONResponse(content={"message": "Metric deleted"})
    raise HTTPException(status_code=404, detail="Metric not found")


@admin_router.get("/api/metrics", dependencies=[Depends(verify_admin_token)])
def get_metrics() -> List[Dict]:
    service = get_metric_service()
    return service.get_metrics()


@admin_router.post("/api/characters", dependencies=[Depends(verify_admin_token)])
def create_character(request: CharacterCreateRequest) -> JSONResponse:
    service = get_character_service()
    character_id = service.add_character(
        name=request.name,
        stats=request.stats,
        image_path=request.image_path
    )
    if character_id > 0:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"id": character_id, "message": "Character created"}
        )
    raise HTTPException(status_code=500, detail="Failed to create character")


@admin_router.put("/api/characters/{character_id}", dependencies=[Depends(verify_admin_token)])
def update_character(character_id: int, request: CharacterUpdateRequest) -> JSONResponse:
    service = get_character_service()
    update_data = request.dict(exclude_unset=True)
    if update_data:
        success = service.change_character(character_id, **update_data)
        if success:
            return JSONResponse(content={"message": "Character updated"})
    raise HTTPException(status_code=404, detail="Character not found")


@admin_router.delete("/api/characters/{character_id}", dependencies=[Depends(verify_admin_token)])
def delete_character(character_id: int) -> JSONResponse:
    service = get_character_service()
    success = service.delete_character(character_id)
    if success:
        return JSONResponse(content={"message": "Character deleted"})
    raise HTTPException(status_code=404, detail="Character not found")


@admin_router.get("/api/characters", dependencies=[Depends(verify_admin_token)])
def get_characters() -> List[CharacterResponse]:
    service = get_character_service()
    return service.get_characters()


@admin_router.get("/api/characters/{character_id}", dependencies=[Depends(verify_admin_token)])
def get_character(character_id: int) -> CharacterResponse:
    service = get_character_service()
    character = service.get_character(character_id)
    if character:
        return character
    raise HTTPException(status_code=404, detail="Character not found")


@admin_router.post("/api/cards", dependencies=[Depends(verify_admin_token)])
def create_card(request: CardCreateRequest) -> JSONResponse:
    service = get_card_service()
    card_id = service.add_card(
        card_text=request.card_text,
        image_path=request.image_path
    )
    if card_id > 0:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"id": card_id, "message": "Card created"}
        )
    raise HTTPException(status_code=500, detail="Failed to create card")


@admin_router.put("/api/cards/{card_id}", dependencies=[Depends(verify_admin_token)])
def update_card(card_id: int, request: CardUpdateRequest) -> JSONResponse:
    service = get_card_service()
    update_data = request.dict(exclude_unset=True)
    if update_data:
        success = service.change_card(card_id, **update_data)
        if success:
            return JSONResponse(content={"message": "Card updated"})
    raise HTTPException(status_code=404, detail="Card not found")


@admin_router.delete("/api/cards/{card_id}", dependencies=[Depends(verify_admin_token)])
def delete_card(card_id: int) -> JSONResponse:
    service = get_card_service()
    success = service.delete_card(card_id)
    if success:
        return JSONResponse(content={"message": "Card deleted"})
    raise HTTPException(status_code=404, detail="Card not found")


@admin_router.get("/api/cards", dependencies=[Depends(verify_admin_token)])
def get_cards() -> List[CardResponse]:
    service = get_card_service()
    return service.get_cards()


@admin_router.get("/api/cards/{card_id}", dependencies=[Depends(verify_admin_token)])
def get_card(card_id: int) -> CardResponse:
    service = get_card_service()
    card = service.get_card(card_id)
    if card:
        return card
    raise HTTPException(status_code=404, detail="Card not found")


@admin_router.post("/api/answers", dependencies=[Depends(verify_admin_token)])
def create_answer(request: AnswerCreateRequest) -> JSONResponse:
    service = get_answer_service()
    answer_id = service.add_answer(
        card_uuid=request.card_uuid,
        answer_text=request.answer_text,
        stats_change=request.stats_change,
        order_index=request.order_index
    )
    if answer_id > 0:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"id": answer_id, "message": "Answer created"}
        )
    raise HTTPException(status_code=500, detail="Failed to create answer")


@admin_router.put("/api/answers/{answer_id}", dependencies=[Depends(verify_admin_token)])
def update_answer(answer_id: int, request: AnswerUpdateRequest) -> JSONResponse:
    service = get_answer_service()
    update_data = request.dict(exclude_unset=True)
    if update_data:
        success = service.change_answer(answer_id, **update_data)
        if success:
            return JSONResponse(content={"message": "Answer updated"})
    raise HTTPException(status_code=404, detail="Answer not found")


@admin_router.delete("/api/answers/{answer_id}", dependencies=[Depends(verify_admin_token)])
def delete_answer(answer_id: int) -> JSONResponse:
    service = get_answer_service()
    success = service.delete_answer(answer_id)
    if success:
        return JSONResponse(content={"message": "Answer deleted"})
    raise HTTPException(status_code=404, detail="Answer not found")


@admin_router.get("/api/answers", dependencies=[Depends(verify_admin_token)])
def get_answers(card_uuid: Optional[str] = None) -> List[AnswerResponse]:
    service = get_answer_service()
    if card_uuid:
        return service.get_answers_to_card(card_uuid)
    return []


@admin_router.get("/api/answers/{answer_id}", dependencies=[Depends(verify_admin_token)])
def get_answer(answer_id: int) -> AnswerResponse:
    service = get_answer_service()
    answer = service.get_answer(answer_id)
    if answer:
        return answer
    raise HTTPException(status_code=404, detail="Answer not found")


@admin_router.post("/api/upload_image", dependencies=[Depends(verify_admin_token)])
async def upload_image(folder: str = Form(...), file: UploadFile = File(...)):
    service = get_image_service()
    image_path = service.add_image(file, folder)
    if image_path:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"path": image_path, "message": "Image uploaded"}
        )
    raise HTTPException(status_code=500, detail="Failed to upload image")
@admin_router.get("/api/images/{folder}", dependencies=[Depends(verify_admin_token)])
def get_images(folder: str):
    service = get_image_service()
    files = service.get_files_in_folder(folder)
    return files


@admin_router.get("/api/resources/bg", dependencies=[Depends(verify_admin_token)])
def get_bg():
    service = get_image_service()
    bg = service.get_bg()
    return {"bg_path": bg}

@admin_router.post("/api/resources/bg", dependencies=[Depends(verify_admin_token)])
def set_bg(request: dict):
    service = get_image_service()
    service.set_bg(request.get("bg_path"))
    return {"success": True}