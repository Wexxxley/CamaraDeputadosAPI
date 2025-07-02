from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

from models.deputado import Deputado
from models.sessao_votacao import SessaoVotacao

class VotoIndividual(SQLModel, table=True):
    """
    Modelo para registrar o voto individual de um Deputado em uma Sessão de Votação.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: Optional[int] = Field(default=None, index=True, unique=True, description="ID do voto nos Dados Abertos (se disponível).")

    id_deputado: int = Field(foreign_key="deputado.id", index=True, description="ID do deputado que votou.")
    id_votacao: int = Field(foreign_key="sessao_votacao.id", index=True, description="ID da sessão de votação.")
    tipo_voto: str = Field(max_length=20, description="Tipo de voto (Sim, Não, Abstenção, Obstrução, Ausente).")

    data_hora_registro: Optional[datetime] = Field(default=None)
    sigla_partido_deputado: Optional[str] = Field(default=None, max_length=10) # Para redundância e otimização, mas pode ser obtido via FK
    uri_deputado: Optional[str] = Field(default=None, max_length=500)

    # Relações
    deputado: Deputado = Relationship(back_populates="votos_individuais")
    votacao: SessaoVotacao = Relationship(back_populates="votos")