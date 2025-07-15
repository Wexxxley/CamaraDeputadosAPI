from http import HTTPStatus
import math
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, func, select
from database import get_session
from dtos.despesa_dtos import DespesaCreate, DespesaResponse, DespesaUpdate
from log.logger_config import get_logger
from models.deputado import Deputado
from models.despesa import Despesa
from utils.pagination import PaginatedResponse, PaginationParams

logger = get_logger("despesas_logger", "log/despesas.log")

despesa_router = APIRouter(prefix="/despesa", tags=["Despesa"])

@despesa_router.get("/get_by_id/{despesa_id}")
def get_despesa_by_id(despesa_id: int, session: Session = Depends(get_session)):

    despesa = session.get(Despesa, despesa_id)
    if not despesa:
        logger.warning(f"Despesa com ID {despesa_id} não encontrada.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Despesa com ID {despesa_id} não encontrada.")
    return despesa

@despesa_router.get("/get_all")
def get_all_despesas(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    id_deputado: Optional[int] = Query(None, description="Filtrar despesas por ID do deputado."),
    ano: Optional[int] = Query(None, description="Filtrar despesas por ano."),
    mes: Optional[int] = Query(None, description="Filtrar despesas por mês.")
):

    statement = select(Despesa)
    if id_deputado:
        statement = statement.where(Despesa.id_deputado == id_deputado)
    if ano:
        statement = statement.where(Despesa.ano == ano)
    if mes:
        statement = statement.where(Despesa.mes == mes)

    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    offset = (pagination.page - 1) * pagination.per_page
    despesas_statement = statement.offset(offset).limit(pagination.per_page)
    despesas = session.exec(despesas_statement).all()

    return PaginatedResponse(
        items=despesas,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=math.ceil(total / pagination.per_page) if total > 0 else 0
    )

@despesa_router.post("/create")
def create_despesa(despesa_data: DespesaCreate, session: Session = Depends(get_session)):

    deputado = session.get(Deputado, despesa_data.id_deputado)
    if not deputado:
        logger.warning(f"Tentativa de criar despesa para deputado inexistente. ID: {despesa_data.id_deputado}")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Deputado com ID {despesa_data.id_deputado} não encontrado."
        )
    
    despesa_db = Despesa.model_validate(despesa_data)
    session.add(despesa_db)
    session.commit()
    session.refresh(despesa_db)
    logger.info(f"Despesa com ID {despesa_db.id} criada para o deputado ID {despesa_db.id_deputado}.")
    
    return despesa_db

@despesa_router.put("/update/{despesa_id}", response_model=DespesaResponse)
def update_despesa(despesa_id: int, despesa_data: DespesaUpdate, session: Session = Depends(get_session)):
    despesa_db = session.get(Despesa, despesa_id)
    if not despesa_db:
        logger.warning(f"Tentativa de atualizar despesa inexistente. ID: {despesa_id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Despesa com ID {despesa_id} não encontrada.")

    update_dict = despesa_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(despesa_db, key, value)
    
    session.add(despesa_db)
    session.commit()
    session.refresh(despesa_db)
    logger.info(f"Despesa com ID {despesa_db.id} atualizada.")
    
    return despesa_db

@despesa_router.delete("/delete/{despesa_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_despesa(despesa_id: int, session: Session = Depends(get_session)):
    despesa_db = session.get(Despesa, despesa_id)
    if not despesa_db:
        logger.warning(f"Tentativa de deletar despesa inexistente. ID: {despesa_id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Despesa com ID {despesa_id} não encontrada.")
    
    session.delete(despesa_db)
    session.commit()
    logger.info(f"Despesa com ID {despesa_id} deletada.")

    return {"message": "Despesa deletada com sucesso."}
