import math
from fastapi import APIRouter, Depends
from sqlmodel import Session, desc, func, select
from database import get_session
from dtos.analise_dtos import DeputadoRankingDespesa, PartidoRankingDespesa, ResumoDeputado
from log.logger_config import get_logger
from models.deputado import Deputado
from models.partido import Partido
from models.voto_individual import VotoIndividual
from utils.pagination import PaginatedResponse, PaginationParams

from utils.querys import get_despesas_deputado_2024_subquery

logger = get_logger("analises_logger", "log/analises.log")

analise_router = APIRouter(prefix="/analise", tags=["Analises"])

@analise_router.get("/ranking/deputados_despesa")
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

@analise_router.get("/ranking/partidos_despesa")
def get_ranking_partidos_despesa(session: Session = Depends(get_session)):
    despesas_subq = get_despesas_deputado_2024_subquery()
    
    statement = (
        select(
            Partido,
            func.sum(despesas_subq.c.total_despesas).label("total_geral_partido")
        )
        .join(Deputado, Partido.id == Deputado.id_partido)
        .join(despesas_subq, Deputado.id == despesas_subq.c.id_deputado)
        .group_by(Partido.id)
        .order_by(desc("total_geral_partido"))
    )
    
    results = session.exec(statement).all()

    ranking = [
        PartidoRankingDespesa(
            id= partido.id,
            id_dados_abertos = partido.id_dados_abertos,
            sigla=partido.sigla,
            nome_completo=partido.nome_completo,
            total_despesas=round(total)
        )
        for partido, total in results
    ]
    return ranking

# 3. Resumo de Atuação de um Deputado
@analise_router.get("/deputados/{id_deputado}/resumo")
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
