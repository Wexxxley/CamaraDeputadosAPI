from sqlmodel import SQLModel, Session, select
from database import engine
import json
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

from models.deputado import Deputado
from models.despesa import Despesa

app = SQLModel()

def salvando_despesas_localmente_json():
    # Primeiro é preciso carregar os deputados na memoria
    with Session(engine) as session:
        statement = select(Deputado)
        deputados = session.exec(statement).all()
    
    despesas_completos = []

    for i, deputado in enumerate(deputados):

        print("Processando deputado:", deputado.nome_eleitoral, "I:", i)
        # É preciso acessar a api das despesas do deputado
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputado.id_dados_abertos}/despesas?ano=2024&itens=1500"
        response = requests.get(url, headers={"accept": "application/json"})
        if response.status_code == 200:
            dados = response.json().get("dados", [])
        else:
            print(f"Erro ao buscar despesas para deputado {deputado.nome}: {response.status_code}")
            dados = []
        despesas_completos.append({
            "id_deputado": deputado.id_dados_abertos,
            "nome_deputado": deputado.nome_eleitoral,
            "despesas": dados
        })

    # Salvar todas as despesas em um arquivo JSON
    with open("despesas_deputados_2024.json", "w", encoding="utf-8") as f:
        json.dump(despesas_completos, f, ensure_ascii=False, indent=2)

def carregar_despesas_json(caminho_arquivo: str) -> List[Dict]:
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

def main():
    arquivo_json = 'data/despesas_deputados_2024.json'
    despesas_base = carregar_despesas_json(arquivo_json)
    
    despesas_completos = []

    for despesa in despesas_base:        
        print("Processando despesa do deputado:", despesa.get('nome_deputado'))
        
        print(despesa)
    #     despesa_combinado = Despesa(
    #         id_dados_abertos=,
    #         sigla=despesa.get("sigla"),
    #         nome_completo=despesa.get("nome"),
    #         uri_logo=detalhes_json.get('uri_logo'),
    #         id_legislativo=detalhes_json.get('id_legislativo'),
    #         situacao=detalhes_json.get('situacao'),
    #         total_membros=detalhes_json.get('total_membros'),
    #         total_posse_legislatura=detalhes_json.get('total_posse_legislatura'),
    #     )
    #     despesas_completos.append(despesa_combinado)

    # with Session(engine) as session:
    #     for despesa in despesas_completos:
    #         session.add(despesa)
        
    #     session.commit()

#  id_dados_abertos: Optional[int] = Field(default=None, index=True, unique=True, description="ID da despesa nos Dados Abertos (se disponível).")

#     id_deputado: int = Field(foreign_key="deputado.id", index=True, description="ID do deputado a quem a despesa pertence.")
#     ano: int = Field(description="Ano da despesa.")
#     mes: int = Field(description="Mês da despesa.")
#     tipo_despesa: str = Field(max_length=300, description="Tipo da despesa (ex: 'Passagens Aéreas', 'Combustíveis').")
#     valor_liquido: float = Field(description="Valor líquido da despesa.")

#     tipo_documento: Optional[str] = Field(default=None, max_length=100)
#     url_documento: Optional[str] = Field(default=None, max_length=500)
#     nome_fornecedor: Optional[str] = Field(default=None, max_length=255)

#     deputado: "Deputado" = Relationship(back_populates="despesas")

salvando_despesas_localmente_json()

# [
#   {
#     "id_deputado": 220593,
#     "nome_deputado": "Abilio Brunini",
#     "despesas": [
#       {
#         "ano": 2024,
#         "mes": 1,
#         "tipoDespesa": "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
#         "codDocumento": 7684463,
#         "tipoDocumento": "Nota Fiscal",
#         "codTipoDocumento": 0,
#         "dataDocumento": "2024-01-04T00:00:00",
#         "numDocumento": "11533012024001",
#         "valorDocumento": 67.3,
#         "urlDocumento": "https://www.camara.leg.br/cota-parlamentar/documentos/publ/3687/2024/7684463.pdf",
#         "nomeFornecedor": "AGUAS CUIABA S.A",
#         "cnpjCpfFornecedor": "14995581000153",
#         "valorLiquido": 67.3,
#         "valorGlosa": 0.0,
#         "numRessarcimento": "",
#         "codLote": 2011692,
#         "parcela": 0
#       },
#       {