from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from database import get_session
from log.logger_config import get_logger
from models.proposicao import Proposicao
from utils.pagination import PaginatedResponse, PaginationParams
import math
from typing import Optional
from dtos.proposicao_dtos import  ProposicaoMaisVotadaDTO
from models.votacao_proposicao import VotacaoProposicao

logger = get_logger("proposicoes_logger", "log/proposicoes.log")
proposicao_router = APIRouter(prefix="/proposicao", tags=["Proposicao"])

# Obtém uma proposição pelo ID
@proposicao_router.get("/get_by_id/{id}")
def get_by_id(id: int, session: Session = Depends(get_session)):
    proposicao = session.get(Proposicao, id)
    if not proposicao:
        raise HTTPException(status_code=404, detail="Proposição não encontrada.")
    return proposicao

# Obtém todas as proposições com paginação e filtros opcionais
@proposicao_router.get("/get_all")
def get_all_proposicoes(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    ano: Optional[int] = Query(None),
    sigla_tipo: Optional[str] = Query(None)
):
    statement = select(Proposicao)

    if ano:
        statement = statement.where(Proposicao.ano == ano)
    if sigla_tipo:
        statement = statement.where(Proposicao.sigla_tipo == sigla_tipo.upper())

    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    offset = (pagination.page - 1) * pagination.per_page
    results = session.exec(statement.offset(offset).limit(pagination.per_page)).all()

    return PaginatedResponse(
        items=results,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=math.ceil(total / pagination.per_page) if total > 0 else 0
    )

# Obtém as 10 proposições mais votadas
@proposicao_router.get("/mais_votadas", response_model=list[ProposicaoMaisVotadaDTO])
def get_proposicoes_mais_votadas(session: Session = Depends(get_session)):
    stmt = (
        select(
            Proposicao.id,
            Proposicao.id_dados_abertos,
            Proposicao.sigla_tipo,
            Proposicao.ano,
            Proposicao.ementa,
            func.count(VotacaoProposicao.id_votacao).label("total_votacoes")
        )
        .join(VotacaoProposicao, VotacaoProposicao.id_proposicao == Proposicao.id)
        .group_by(Proposicao.id)
        .order_by(func.count(VotacaoProposicao.id_votacao).desc())
        .limit(10)
    )

    results = session.exec(stmt).all()
    return results