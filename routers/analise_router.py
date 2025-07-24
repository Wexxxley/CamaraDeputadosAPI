from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, func, select
from database import get_session
from dtos.analise_dtos import PartidoRankingDespesa
from dtos.ranking_deputados_atuantes_dtos import DeputadoRankingDTO
from log.logger_config import get_logger
from models.deputado import Deputado
from models.despesa import Despesa
from models.partido import Partido

from models.votacao_proposicao import VotacaoProposicao
from models.voto_individual import VotoIndividual
from utils.pagination import PaginatedResponse, PaginationParams
from utils.querys import get_despesas_deputado_2024_subquery

logger = get_logger("analises_logger", "log/analises.log")

analise_router = APIRouter(prefix="/analise", tags=["Analises"])

@analise_router.get("/ranking/partidos_despesa")
def get_ranking_partidos_despesa(session: Session = Depends(get_session)):
    """
    Retorna um ranking de partidos ordenado pela soma total das despesas de seus deputados em 2024. 
    
    Entidades: Partido, Deputado e Despesa.
    """
    
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



@analise_router.get("/comparativo_estados")
async def comparativo_gastos_estados(
    session: Session = Depends(get_session),
    ano: int = Query(2024, description="Ano de referência para análise", ge=2000),
    uf: Optional[str] = Query(
        None,
        description="Filtrar por sigla de UF específica (ex: 'SP')",
        max_length=2,
        regex="^[A-Z]{2}$"
    )
):
    """
    Agrupa os gastos parlamentares por estado, retornando o gasto 
    total, a média e a quantidade de despesas. 
    
    Entidades: Deputado e Despesa.
    """
    try:
        stmt = (
            select(
                Deputado.sigla_uf,
                func.sum(Despesa.valor_liquido).label("total_gasto"),
                func.avg(Despesa.valor_liquido).label("media_gasto"),
                func.count(Despesa.id).label("quantidade"),
                func.count(Deputado.id.distinct()).label("total_deputados")
            )
            .join(Despesa, Despesa.id_deputado == Deputado.id)
            .where(Despesa.ano == ano)
        )

        if uf:
            stmt = stmt.where(Deputado.sigla_uf == uf.upper())

        stmt = stmt.group_by(Deputado.sigla_uf).order_by(desc("total_gasto"))
        results = session.exec(stmt).all()

        return [
            {
                "uf": sigla_uf,
                "total_gasto": round(total, 2) if total else 0,
                "media_gasto": round(media, 2) if media else 0,
                "quantidade": quantidade,
                "total_deputados": total_deputados
            }
            for sigla_uf, total, media, quantidade, total_deputados in results
        ]

    except Exception as e:
        logger.error(f"Erro ao gerar comparativo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar análise de gastos"
        )