from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

class VotoIndividual(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_dados_abertos: Optional[int] = Field(default=None, index=True, unique=True)

    id_votacao: int = Field(foreign_key="sessaovotacao.id", index=True)
    id_deputado: int = Field(foreign_key="deputado.id", index=True)
    id_proposicao: int = Field(foreign_key="proposicao.id", index=True)
    
    tipo_voto: str = Field(max_length=20, description="Sim, Não, Abstenção, Obstrução, Ausente")
    data_hora_registro: Optional[datetime] = Field(default=None)
    sigla_partido_deputado: Optional[str] = Field(default=None, max_length=50)
    uri_deputado: Optional[str] = Field(default=None, max_length=500)

    votacao: "SessaoVotacao" = Relationship(back_populates="votos")
    deputado: "Deputado" = Relationship(back_populates="votos_individuais")
    proposicao: "Proposicao" = Relationship(back_populates="votos_individuais")
