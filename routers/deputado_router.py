from http import HTTPStatus
import math
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, func, select
from database import get_session
from dtos.deputado_dtos import DeputadoCreateWithGabinete, DeputadoResponseWithGabinete, GabineteResponse
from log.logger_config import get_logger
from models.deputado import Deputado
from models.despesa import Despesa
from models.gabinete import Gabinete
from models.partido import Partido
from models.voto_individual import VotoIndividual
from utils.pagination import PaginatedResponse, PaginationParams
from sqlalchemy.orm import selectinload

logger = get_logger("deputados_logger", "log/deputados.log")

deputado_router = APIRouter(prefix="/deputado", tags=["Deputado"])

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

@deputado_router.post("/create")
def create_deputado_com_gabinete(
    deputado_data: DeputadoCreateWithGabinete, 
    session: Session = Depends(get_session)
):
    # Verificando se o deputado já existe para evitar duplicatas
    deputado_existente = session.exec(
        select(Deputado).where(Deputado.id_dados_abertos == deputado_data.id_dados_abertos)
    ).first()
    if deputado_existente:
        logger.warning(f"Deputado com o id_dados_abertos '{deputado_data.id_dados_abertos}' já existe.")
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Deputado com o id_dados_abertos '{deputado_data.id_dados_abertos}' já existe."
        )
    
    #Verificando se o partido existe
    partido = session.exec(
        select(Partido).where(deputado_data.id_partido == Partido.id)        
    ).first()
    if not partido:
        logger.warning(f"Partido com o id '{deputado_data.id_partido}' inexistente.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Partido com o id '{deputado_data.id_partido}' inexistente."
        )

    if deputado_data.sigla_partido.upper() != partido.sigla.upper():
        logger.warning(f"Sigla do partido com id '{partido.id}' inconsistente com a sigla fornecida.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Sigla do partido com id '{partido.id}' inconsistente com a sigla fornecida."
        )

    deputado_dict = deputado_data.model_dump(exclude={'gabinete'})
    deputado_db = Deputado(**deputado_dict)
  
    session.add(deputado_db)
    session.flush()
    session.refresh(deputado_db)

    gabinete_db = Gabinete(
        **deputado_data.gabinete.model_dump(),
        id_deputado=deputado_db.id
    )
    session.add(gabinete_db)
   
    session.commit()

    session.refresh(deputado_db)
    session.refresh(gabinete_db)

    deputado_response = DeputadoResponseWithGabinete.from_model(deputado_db, gabinete_db)

    logger.info(f"Deputado com id {deputado_response.id} criado com sucesso.")
    return deputado_response

@deputado_router.put("/update/{id_dados_abertos}", response_model=DeputadoResponseWithGabinete)
def update_deputado(
    id_deputado: int,
    deputado_data: DeputadoCreateWithGabinete,
    session: Session = Depends(get_session)
):
   
    deputado_db = session.exec(
        select(Deputado)
        .where(Deputado.id == id_deputado)
        .options(selectinload(Deputado.gabinete))
    ).first()

    if not deputado_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Deputado com o id '{id_deputado}' não encontrado."
        )

    partido = session.exec(select(Partido).where(Partido.id == deputado_data.id_partido)).first()
    if not partido:
        logger.warning(f"Partido com o id '{deputado_data.id_partido}' é inexistente.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Partido com o id '{deputado_data.id_partido}' é inexistente."
        )
    if deputado_data.sigla_partido.upper() != partido.sigla.upper():
        logger.warning(f"Sigla do partido inconsistente com o id do partido fornecido.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Sigla do partido inconsistente com o id do partido fornecido."
        )

    deputado_update_dict = deputado_data.model_dump(exclude={'gabinete'})
    for key, value in deputado_update_dict.items():
        setattr(deputado_db, key, value)

    gabinete_update_dict = deputado_data.gabinete.model_dump()
    if deputado_db.gabinete:
        for key, value in gabinete_update_dict.items():
            setattr(deputado_db.gabinete, key, value)
    else:
        novo_gabinete = Gabinete(**gabinete_update_dict, id_deputado=deputado_db.id_dados_abertos)
        session.add(novo_gabinete)

    session.add(deputado_db)
    session.commit()
    session.refresh(deputado_db)

    gabinete_response = GabineteResponse.from_model(deputado_db.gabinete) if deputado_db.gabinete else None
    deputado_response = DeputadoResponseWithGabinete.from_model(deputado_db, gabinete_response)
    
    logger.info(f"Deputado com id {deputado_response.id} atualizado com sucesso.")
    return deputado_response

@deputado_router.delete("/delete/{id_deputado}")
def delete_deputado(
    id_deputado: int,
    session: Session = Depends(get_session)
):

    deputado_db = session.exec(
        select(Deputado).where(Deputado.id == id_deputado)
    ).first()

    if not deputado_db:
        logger.warning(f"Nao foi possivel deletar deputado. Id deputado {id_deputado} nao encontrado.")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Deputado com o id '{id_deputado}' não encontrado."
        )

    despesas_a_deletar = session.exec(
        select(Despesa).where(Despesa.id_deputado == id_deputado)
    ).all()
    for despesa in despesas_a_deletar:
        session.delete(despesa)
    
    votos_a_deletar = session.exec(
        select(VotoIndividual).where(VotoIndividual.id_deputado == id_deputado)
    ).all()
    for voto in votos_a_deletar:
        session.delete(voto)
    
    gabinete_a_deletar = session.exec(
        select(Gabinete).where(Gabinete.id_deputado == id_deputado)
    ).first()
    if gabinete_a_deletar:
        session.delete(gabinete_a_deletar)

    session.delete(deputado_db)

    session.commit()

    logger.info(f"Deputado deletado com sucesso.")
    return {"message": "Deputado deletado com sucesso."}