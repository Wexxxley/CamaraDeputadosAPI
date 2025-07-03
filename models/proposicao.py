from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

class Proposicao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: int = Field(index=True, unique=True, description="ID da proposição nos Dados Abertos da Câmara.")
    sigla_tipo: str = Field(max_length=10, description="Sigla do tipo de proposição (PL, PEC, MPV, PLP, etc.).")
    ano: int = Field(description="Ano da proposição.")

    ementa: Optional[str] = Field(default=None, description="Ementa (resumo) da proposição.")
    data_apresentacao: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=50) # Ex: "Aprovado", "Arquivado"
    url_inteiro_teor: Optional[str] = Field(default=None, max_length=500)

    # Relações: uma proposição pode estar em várias votações (associativa)
    votos_individuais: List["VotoIndividual"] = Relationship(back_populates="proposicao")

    votacoes_proposicao: List["VotacaoProposicao"] = Relationship(back_populates="proposicao")