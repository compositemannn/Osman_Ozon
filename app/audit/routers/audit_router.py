from datetime import date

from fastapi import APIRouter, Depends

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
    handler = AuditHandler(repo=repo)
    return await handler.get_or_create_day(date)


@router.post("/action", response_model=AuditActionResponse)
async def create(
    payload: AuditActionDTOs_schemas.AuditActionCreate,
    repo: AuditRepository = Depends(get_repo_obj),
) -> AuditActionResponse:
    handler = AuditHandler(repo=repo, payload=payload.model_dump())
    return await handler.create_action()


@router.patch("/action/{id}", response_model=AuditActionResponse)
async def update(
    id: int,
    payload: AuditActionDTOs_schemas.AuditActionUpdate,
    repo: AuditRepository = Depends(get_repo_obj),
) -> AuditActionResponse:
    handler = AuditHandler(repo=repo, payload=payload.model_dump(exclude_unset=True))
    return await handler.update_action(id)


@router.delete("/action/{id}", response_model=DeleteResponseDTO)
async def delete(id: id, repo: AuditRepository = Depends(get_repo_obj)):
    handler = AuditHandler(repo=repo)
    return await handler.delete_action(id)
