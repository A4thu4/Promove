import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.db.session import get_db
from backend.app.models.batch_history import BatchHistory
from backend.app.models.user import User
from backend.app.schemas.evolution import (
    BatchCalculationOutput,
    BatchHistoryItem,
    BatchRowResult,
)
from backend.app.services.batch_calculator import (
    export_filename,
    run_batch,
    to_excel_bytes,
)

router = APIRouter()
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "").lower() not in ("true", "1"),
)


async def _process_upload(
    file: UploadFile, is_ueg: bool, apo_especial: bool
) -> BatchCalculationOutput:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido.")
    content = await file.read()
    try:
        return run_batch(
            file_bytes=content,
            filename=file.filename,
            is_ueg=is_ueg,
            apo_especial=apo_especial,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/calculate", response_model=BatchCalculationOutput)
@limiter.limit("30/minute")
async def batch_calculate(
    request: Request,
    file: UploadFile = File(...),
    is_ueg: bool = Form(False),
    apo_especial: bool = Form(False),
):
    """Simula o lote (não persiste)."""
    return await _process_upload(file, is_ueg, apo_especial)


@router.post("/calculate-save", response_model=BatchCalculationOutput)
@limiter.limit("20/minute")
async def batch_calculate_and_save(
    request: Request,
    file: UploadFile = File(...),
    is_ueg: bool = Form(False),
    apo_especial: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calcula e persiste o lote no histórico do usuário logado."""
    output = await _process_upload(file, is_ueg, apo_especial)

    record = BatchHistory(
        user_id=current_user.id,
        filename=output.filename,
        is_ueg=output.is_ueg,
        apo_especial=output.apo_especial,
        total_linhas=output.total_linhas,
        resultados=[r.model_dump(mode="json") for r in output.resultados],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    output.id = record.id
    return output


@router.get("/history", response_model=list[BatchHistoryItem])
def list_batch_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(BatchHistory)
        .filter(BatchHistory.user_id == current_user.id)
        .order_by(BatchHistory.created_at.desc())
        .all()
    )
    return [
        BatchHistoryItem(
            id=r.id,
            created_at=r.created_at.isoformat() if r.created_at else "",
            filename=r.filename or "",
            is_ueg=bool(r.is_ueg),
            apo_especial=bool(r.apo_especial),
            total_linhas=int(r.total_linhas or 0),
        )
        for r in rows
    ]


def _load_owned_batch(
    batch_id: int, db: Session, current_user: User
) -> BatchHistory:
    record = (
        db.query(BatchHistory)
        .filter(
            BatchHistory.id == batch_id,
            BatchHistory.user_id == current_user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    return record


@router.get("/history/{batch_id}", response_model=BatchCalculationOutput)
def get_batch_detail(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = _load_owned_batch(batch_id, db, current_user)
    resultados = [BatchRowResult.model_validate(r) for r in (record.resultados or [])]
    return BatchCalculationOutput(
        id=record.id,
        filename=record.filename or "",
        total_linhas=record.total_linhas or 0,
        is_ueg=bool(record.is_ueg),
        apo_especial=bool(record.apo_especial),
        resultados=resultados,
    )


@router.get("/history/{batch_id}/export")
def export_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = _load_owned_batch(batch_id, db, current_user)
    output = BatchCalculationOutput(
        id=record.id,
        filename=record.filename or "",
        total_linhas=record.total_linhas or 0,
        is_ueg=bool(record.is_ueg),
        apo_especial=bool(record.apo_especial),
        resultados=[BatchRowResult.model_validate(r) for r in (record.resultados or [])],
    )
    data = to_excel_bytes(output)
    filename = export_filename(output.filename or f"lote-{batch_id}")
    return Response(
        content=data,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export")
def export_batch_stateless(output: BatchCalculationOutput):
    data = to_excel_bytes(output)
    filename = export_filename(output.filename or "lote")
    return Response(
        content=data,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
