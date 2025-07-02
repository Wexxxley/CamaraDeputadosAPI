from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

class SessaoVotacao(SQLModel, table=True):
    """
    Modelo principal para representar uma Sessão de Votação na Câmara dos Deputados.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: int = Field(index=True, unique=True, description="ID da votação nos Dados Abertos da Câmara.")
    data_hora_registro: datetime = Field(description="Data e hora do registro da votação.")
    descricao: str = Field(max_length=500, description="Descrição da votação.")

    data_hora_ultima_abertura: Optional[datetime] = Field(default=None)
    sigla_orgao: Optional[str] = Field(default=None, max_length=50)
    aprovacao: Optional[str] = Field(default=None, max_length=50) # Ex: "Aprovada", "Rejeitada", "Prejudicada"
    descrico_ultima_abertura_votacao: Optional[str] = Field(default=None, max_length=500)
    uri: Optional[str] = Field(default=None, max_length=500)

    # Relações: uma votação pode ter múltiplos votos individuais e múltiplas proposições
    votos: List["VotoIndividual"] = Relationship(back_populates="votacao")
    votacaoProposicao: List["VotacaoProposicao"] = Relationship(back_populates="sessao_votacao")