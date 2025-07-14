from http import HTTPStatus
import math
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, func, select
from database import get_session
from dtos.deputado_dtos import DeputadoResponseWithGabinete, GabineteResponse
from log.logger_config import get_logger
from models.deputado import Deputado
from pagination import PaginatedResponse, PaginationParams
from sqlalchemy.orm import selectinload

logger = get_logger("deputados_logger", "log/deputados.log")

deputado_router = APIRouter(prefix="/deputado", tags=["deputado"])

@deputado_router.get("/get_by_id/{deputado_id}")
def get_by_id(deputado_id: int, session = Depends(get_session)):
    
    statement = select(Deputado).where(Deputado.id == deputado_id).options(
        selectinload(Deputado.gabinete)
    )
    deputado = session.exec(statement).first()

    if not deputado:
        logger.warning(f"Deputado com ID {deputado_id} nao encontrado.")
        raise HTTPException(status_code=404, detail=f"Deputado com ID {deputado_id} nao encontrado.")

    gabinete_response = None
    if deputado.gabinete:
        gabinete_response = GabineteResponse.from_model(deputado.gabinete)

    deputado_response = DeputadoResponseWithGabinete.from_model(deputado, gabinete_response)

    return deputado_response
@deputado_router.get("/get_all", response_model=PaginatedResponse[DeputadoResponseWithGabinete])
def get_all(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    uf: Optional[str] = Query(None, description="Filtrar por sigla da UF (ex: PR, SP)"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo (M ou F)"),
    partido: Optional[str] = Query(None, description="Filtrar por sigla do partido (ex: PT, PL)")
):
    statement = select(Deputado).options(selectinload(Deputado.gabinete))

    if uf:
        statement = statement.where(Deputado.sigla_uf == uf.upper())
    if sexo:
        statement = statement.where(Deputado.sexo == sexo.upper())
    if partido:
        statement = statement.where(Deputado.sigla_partido == partido.upper())

    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    offset = (pagination.page - 1) * pagination.per_page
    deputados_statement = statement.offset(offset).limit(pagination.per_page)
    
    deputados_db = session.exec(deputados_statement).all()

    items_response = [
        DeputadoResponseWithGabinete.from_model(
            deputado=dep,
            gabinete=GabineteResponse.from_model(dep.gabinete) if dep.gabinete else None
        )
        for dep in deputados_db
    ]

    return PaginatedResponse(
        items=items_response, 
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=math.ceil(total / pagination.per_page) if total > 0 else 0
    )

# @deputado_router.post("/create")
# async def create_deputado()

# @deputado_router.delete("/delete/{deputado_id}")
# async def delete(
#     deputado_id: int,
#     session: AsyncSession = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     # Autorização
#     if not current_user.is_admin:
#         raise HTTPException(
#             status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
#         )

#     deputado = await session.get(deputado, deputado_id)
#     if not deputado:
#         raise HTTPException(status_code=404, detail="deputado não encontrado")

#     await session.delete(deputado)
#     await session.commit()

#     return {"message": "deputado deletado com sucesso"}