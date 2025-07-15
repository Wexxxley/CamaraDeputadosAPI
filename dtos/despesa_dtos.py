from sqlmodel import SQLModel
from typing import Optional
from pydantic import Field, HttpUrl

class DespesaResponse(SQLModel):
    id: int
    id_deputado: int
    ano: int
    mes: int
    tipo_despesa: str
    valor_liquido: float
    tipo_documento: Optional[str] = None
    url_documento: Optional[str] = None
    nome_fornecedor: Optional[str] = None

class DespesaCreate(SQLModel):
    id_deputado: int = Field(..., description="ID do deputado a quem a despesa pertence.")
    ano: int = Field(..., ge=1900, le=2100, description="Ano da despesa.")
    mes: int = Field(..., ge=1, le=12, description="Mês da despesa.")
    tipo_despesa: str
    valor_liquido: float
    tipo_documento: Optional[str] = None
    url_documento: Optional[str] = None
    nome_fornecedor: Optional[str] = None

class DespesaUpdate(SQLModel):
    ano: Optional[int] = Field(default=None, ge=1900, le=2100)
    mes: Optional[int] = Field(default=None, ge=1, le=12)
    tipo_despesa: Optional[str] = None
    valor_liquido: Optional[float] = None
    tipo_documento: Optional[str] = None
    url_documento: Optional[str] = None
    nome_fornecedor: Optional[str] = None
