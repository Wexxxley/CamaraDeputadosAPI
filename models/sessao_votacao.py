from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

class SessaoVotacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: int = Field(index=True, unique=True, description="ID da votação nos Dados Abertos da Câmara.")
    data_hora_registro: datetime = Field(description="Data e hora do registro da votação.")
    descricao: str = Field(description="Descrição da votação.")

    sigla_orgao: Optional[str] = Field(default=None, max_length=50)
    aprovacao: Optional[str] = Field(default=None, max_length=50) # Ex: "Aprovada", "Rejeitada", "Prejudicada"
    descrico_ultima_abertura_votacao: Optional[str] = Field(default=None, max_length=500)
    uri: Optional[str] = Field(default=None, max_length=500)

    votacoes_proposicao: List["VotacaoProposicao"] = Relationship(back_populates="sessao_votacao")
    
    votos: List["VotoIndividual"] = Relationship(back_populates="votacao")

