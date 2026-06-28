from datetime import date
from fastapi import APIRouter, Body, Depends, status
import app.audit.schemas.AuditActionDTOs as AuditActionDTOs_schemas
import app.audit.schemas.AuditDayDTO as AuditDayDTO_schemas
from app.audit.repositories.audit_repo import AuditRepository
from app.audit.repositories.dependencies import get_repo_obj
from app.audit.schemas.AuditActionDTOs import AuditActionResponse, DeleteResponseDTO
from app.audit.schemas.AuditDayDTO import AuditDayFullResponse
from app.audit.services.handle_audit import AuditHandler

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{date}", response_model=AuditDayFullResponse)
async def get(
    date: date, repo: AuditRepository = Depends(get_repo_obj)
) -> AuditDayFullResponse:
    service = AuditHandler(repo=repo)
    return await service.get_or_create_day(date)


@router.post("/action", response_model=AuditActionResponse)
async def create(
    payload: AuditActionDTOs_schemas.AuditActionCreate,
    repo: AuditRepository = Depends(get_repo_obj),
) -> AuditActionResponse:
    service = AuditHandler(repo=repo, payload=payload.model_dump())
    return await service.create_action()


@router.patch("/action/{id}", response_model=AuditActionResponse)
async def update(
    id: id,
    payload: AuditActionDTOs_schemas.AuditActionUpdate,
    repo: AuditRepository = Depends(get_repo_obj),
) -> AuditActionResponse:
    service = AuditHandler(repo=repo, payload=payload.model_dump(exclude_unset=True))
    return await service.update_action(id)


@router.delete("/action/{id}", response_model=DeleteResponseDTO)
async def delete(id: id, repo: AuditRepository = Depends(get_repo_obj)):
    service = AuditHandler(repo=repo)
    return await service.delete_action(id)
