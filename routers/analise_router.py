from fastapi import APIRouter, Depends
from sqlmodel import Session, desc, func, select
from database import get_session
from dtos.analise_dtos import PartidoRankingDespesa
from log.logger_config import get_logger
from models.deputado import Deputado
from models.partido import Partido

from utils.querys import get_despesas_deputado_2024_subquery

logger = get_logger("analises_logger", "log/analises.log")

analise_router = APIRouter(prefix="/analise", tags=["Analises"])

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