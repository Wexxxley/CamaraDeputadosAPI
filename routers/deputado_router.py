import math
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, desc, func, select
from database import get_session
from dtos.analise_dtos import DeputadoRankingDespesa, ResumoDeputado
from dtos.deputado_dtos import DeputadoResponseWithGabinete, GabineteResponse
from log.logger_config import get_logger
from models.deputado import Deputado
from models.voto_individual import VotoIndividual
from utils.pagination import PaginatedResponse, PaginationParams
from models.sessao_votacao import SessaoVotacao
from models.votacao_proposicao import VotacaoProposicao
from models.proposicao import Proposicao
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from dtos.deputado_dtos import DeputadoMaisVotouSimDTO
from sqlalchemy.orm import selectinload

from utils.querys import get_despesas_deputado_2024_subquery

logger = get_logger("deputados_logger", "log/deputados.log")

deputado_router = APIRouter(prefix="/deputado", tags=["Deputado"])

# Endpoint para obter um deputado por ID com detalhes do gabinete
@deputado_router.get("/get_by_id/{deputado_id}")
def get_by_id(deputado_id: int, session: Session = Depends(get_session)):
    
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

# Endpoint para obter todos os deputados com paginação e filtros
@deputado_router.get("/get_all")
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

# Endpoint para obter resumo de um deputado específico
@deputado_router.get("/deputados/{id_deputado}/resumo")
def get_resumo_deputado(id_deputado: int, session: Session = Depends(get_session)):
    
    despesas_subq = get_despesas_deputado_2024_subquery()
    gasto_statement = select(despesas_subq.c.total_despesas).where(despesas_subq.c.id_deputado == id_deputado)
    total_gasto = session.exec(gasto_statement).first() or 0.0

    sessoes_votadas_statement = select(func.count(VotoIndividual.id_votacao.distinct())).where(VotoIndividual.id_deputado == id_deputado)
    sessoes_votadas = session.exec(sessoes_votadas_statement).one()
    
    return ResumoDeputado(
        id=id_deputado,
        sessoes_votadas=sessoes_votadas,
        total_gasto_2024=total_gasto
    )

# Endpoint para obter o ranking dos deputados por despesas em 2024
@deputado_router.get("/ranking/deputados_despesa")
def get_ranking_deputados_despesa(pagination: PaginationParams = Depends(), session: Session = Depends(get_session)):
    despesas_subq = get_despesas_deputado_2024_subquery()

    statement = (
        select(
            Deputado,
            func.coalesce(despesas_subq.c.total_despesas, 0.0).label("total_despesas")
        )
        .join(despesas_subq, Deputado.id == despesas_subq.c.id_deputado, isouter=True)
        .order_by(desc(func.coalesce(despesas_subq.c.total_despesas, 0.0)))
    )
    
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    offset = (pagination.page - 1) * pagination.per_page
    analise_statement = statement.offset(offset).limit(pagination.per_page)

    results = session.exec(analise_statement).all()

    ranking = [
        DeputadoRankingDespesa(
            id=dep.id,
            id_dados_abertos=dep.id_dados_abertos,
            nome_eleitoral=dep.nome_eleitoral,
            sigla_partido=dep.sigla_partido,
            sigla_uf=dep.sigla_uf,
            url_foto=dep.url_foto,
            sexo=dep.sexo,
            total_despesas= round(total_despesas, 2)
        )
        for dep, total_despesas in results
    ]
    
    return PaginatedResponse(
        items=ranking, 
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=math.ceil(total / pagination.per_page) if total > 0 else 0
    )

# Ranking dos Deputados que mais votaram "Sim" em Projetos de Lei (PL)
@deputado_router.get("/ranking/deputados/votos_sim_pl", response_model=List[DeputadoMaisVotouSimDTO])
def ranking_votos_sim_em_pl(session: Session = Depends(get_session)):
    stmt = (
        select(
            Deputado.id.label("id_deputado"),
            Deputado.nome_eleitoral,
            Deputado.sigla_partido,
            Deputado.sigla_uf,
            func.count(VotoIndividual.id).label("total_votos_sim")
        )
        .join(VotoIndividual, VotoIndividual.id_deputado == Deputado.id)
        .join(SessaoVotacao, SessaoVotacao.id == VotoIndividual.id_votacao)
        .join(VotacaoProposicao, VotacaoProposicao.id_votacao == SessaoVotacao.id)
        .join(Proposicao, Proposicao.id == VotacaoProposicao.id_proposicao)
        .where(
            VotoIndividual.tipo_voto.ilike("Sim"),
            Proposicao.sigla_tipo == "PL"
        )
        .group_by(
            Deputado.id,
            Deputado.nome_eleitoral,
            Deputado.sigla_partido,
            Deputado.sigla_uf
        )
        .order_by(func.count(VotoIndividual.id).desc())
        .limit(10)
    )

    results = session.exec(stmt).all()
    return [DeputadoMaisVotouSimDTO(**r._asdict()) for r in results]
