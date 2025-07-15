from http import HTTPStatus
from fastapi import HTTPException
from pydantic import field_validator
from sqlmodel import Field, SQLModel
from typing import Optional

from models.deputado import Deputado
from models.gabinete import Gabinete

class GabineteResponse(SQLModel):
    id: Optional[int]
    nome: Optional[str]
    predio: Optional[str]
    sala: Optional[str] 
    andar: Optional[str] 
    telefone: Optional[str]
    email: Optional[str]

    @classmethod
    def from_model(cls, gabinete: Gabinete):
        return cls(
            id=gabinete.id,
            nome=gabinete.nome,
            predio=gabinete.predio,
            sala=gabinete.sala,
            andar=gabinete.andar,
            telefone=gabinete.telefone,
            email=gabinete.email
        )

class DeputadoResponseWithGabinete(SQLModel):
    id: Optional[int]
    id_dados_abertos: Optional[int]
    nome_civil: Optional[str]
    nome_eleitoral: Optional[str]
    sigla_partido: Optional[str]
    sigla_uf: Optional[str]
    id_partido: Optional[int]
    id_legislativo: Optional[int]
    url_foto: Optional[str]
    sexo: Optional[str]
    gabinete: Optional[GabineteResponse] = None

    @classmethod
    def from_model(cls, deputado: Deputado, gabinete: Optional[GabineteResponse]):
        return cls(
            id=deputado.id,
            id_dados_abertos=deputado.id_dados_abertos,
            nome_civil=deputado.nome_civil,
            nome_eleitoral=deputado.nome_eleitoral,
            sigla_partido=deputado.sigla_partido,
            sigla_uf=deputado.sigla_uf,
            id_partido=deputado.id_partido,
            id_legislativo=deputado.id_legislativo,
            url_foto=deputado.url_foto,
            sexo=deputado.sexo,
            gabinete=gabinete 
        )

class GabineteCreate(SQLModel):
    nome: str
    andar: str
    sala: str
    predio: str
    telefone: str
    email: str

class DeputadoCreateWithGabinete(SQLModel):
    id_dados_abertos: int = Field(..., description="ID único do deputado na API de Dados Abertos.")
    nome_civil: str
    nome_eleitoral: str
    sigla_partido: str
    sigla_uf: str = Field(..., min_length=2, max_length=2, description="Sigla do estado com 2 caracteres.")
    id_partido: int
    id_legislativo: int
    url_foto: str 
    sexo: str = Field(..., description="Deve ser 'M' para Masculino ou 'F' para Feminino.")
    gabinete: GabineteCreate 

    @field_validator("sexo")
    @classmethod
    def valida_sexo(cls, sexo: str):
        sexo_upper = sexo.upper() 
        if sexo_upper not in ("M", "F"):
            raise HTTPException(status_code=400, detail='O sexo deve ser "M" ou "F".')
        return sexo_upper
    
    @field_validator("sigla_partido", "sigla_uf")
    @classmethod
    def upper_sigla(cls, sigla: str):
        return sigla.upper()
