from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

class PartidoPolitico(SQLModel, table=True):
    """
    Modelo para representar um Partido Político.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: int = Field(index=True, unique=True, description="ID do partido nos Dados Abertos da Câmara.")
    sigla: str = Field(max_length=10, unique=True, description="Sigla do partido político.")
    nome_completo: str = Field(max_length=255, description="Nome completo do partido político.")

    uri_logo: Optional[str] = Field(default=None, max_length=500)
    id_legislativo: Optional[int] = Field(default=None)
    situacao: Optional[str] = Field(default=None, max_length=50, description="Ex: 'Ativo', 'Inativo'")
    total_membros: Optional[int] = Field(default=None)
    total_posse_legislatura: Optional[int] = Field(default=None, description="Total de membros do partido na legislatura atual.")
