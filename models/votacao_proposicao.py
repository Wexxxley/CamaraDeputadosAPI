from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from models.proposicao import Proposicao
from models.sessao_votacao import SessaoVotacao

class VotacaoProposicao(SQLModel, table=True):
    """
    Tabela associativa para relacionar Votações com Proposições.
    Uma votação pode envolver várias proposições e uma proposição pode ser votada em várias sessões.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    id_proposicao: int = Field(foreign_key="proposicao.id", index=True, description="ID da proposição associada.")
    id_votacao: int = Field(foreign_key="sessao_votacao.id", index=True, description="ID da sessão de votação associada.")
    tipo_relacao: Optional[str] = Field(default=None, max_length=50, description="Tipo de relação entre a votação e a proposição (ex: 'PRINCIPAL', 'AFETADA').")

    proposicao: Proposicao = Relationship(back_populates="votacoes_relacionadas")
    sessao_votacao: SessaoVotacao = Relationship(back_populates="proposicoes_votadas")