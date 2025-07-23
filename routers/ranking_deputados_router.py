from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from database import get_session
from dtos.ranking_deputados_atuantes_dtos import DeputadoRankingDTO
from models.voto_individual import VotoIndividual
from models.votacao_proposicao import VotacaoProposicao
from models.deputado import Deputado
from utils.pagination import PaginationParams, PaginatedResponse

deputado_atuantes_router = APIRouter(
    prefix="/deputado",
    tags=["Deputado"]
)

# Obtém o ranking dos deputados mais atuantes 
@deputado_atuantes_router.get("/ranking/atuantes", response_model=PaginatedResponse[DeputadoRankingDTO])
def get_ranking_deputados__mais_atuantes(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session)
):
    stmt = (
        select(
            Deputado.id,
            Deputado.nome_eleitoral,
            Deputado.sigla_partido,
            Deputado.sigla_uf,
            func.count(func.distinct(VotoIndividual.id_votacao)).label("total_votacoes"),
            func.count(func.distinct(VotacaoProposicao.id_proposicao)).label("total_proposicoes")
        )
        .join(VotoIndividual, VotoIndividual.id_deputado == Deputado.id)
        .join(VotacaoProposicao, VotacaoProposicao.id_votacao == VotoIndividual.id_votacao)
        .group_by(Deputado.id)
        .order_by(func.count(func.distinct(VotoIndividual.id_votacao)).desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )

    results = session.exec(stmt).all()

    # contar total geral para paginação
    count_stmt = (
        select(func.count(func.distinct(Deputado.id)))
        .join(VotoIndividual, VotoIndividual.id_deputado == Deputado.id)
        .join(VotacaoProposicao, VotacaoProposicao.id_votacao == VotoIndividual.id_votacao)
    )
    total = session.exec(count_stmt).scalar_one()

    items = [
        DeputadoRankingDTO(
            id=r[0],
            nome_eleitoral=r[1],
            sigla_partido=r[2],
            sigla_uf=r[3],
            total_votacoes=r[4],
            total_proposicoes=r[5]
        ) for r in results
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=(total // pagination.per_page + int(total % pagination.per_page > 0))
    )
