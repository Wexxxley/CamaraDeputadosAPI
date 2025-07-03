from sqlmodel import SQLModel, Session
from database import engine
import json
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

app = SQLModel()

def carregar_deputados_json(caminho_arquivo: str) -> List[Dict]:
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get("dados", [])
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não é um JSON válido.")
        return []

def buscar_detalhes_deputado_xml(uri: str) -> Optional[Dict]:
    try:
        headers = {'accept': 'application/xml'}
        response = requests.get(uri, headers=headers)

        if response.status_code == 200:
            root = ET.fromstring(response.content) # root armazena todo o xml            
       
            dados = root.find('.//dados')
            nome_civil = dados.findtext('nomeCivil')
            nome_eleitoral = dados.findtext('ultimoStatus/nomeEleitoral')
            sexo = dados.findtext('sexo')
            
            detalhes = {
                "nome_civil": nome_civil,
                "nome_eleitoral": nome_eleitoral,
                "sexo": sexo
            }

            return detalhes
        else:
            print(f"  - Falha ao buscar dados da URI {uri}. Status: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  - Erro de conexão ao acessar {uri}: {e}")
        return None
    except ET.ParseError:
        print(f"  - Falha ao analisar o XML da URI {uri}.")
        return None

def main():
    arquivo_json = 'data/deputados_57.json'
    deputados_base = carregar_deputados_json(arquivo_json)
    
    if not deputados_base:
        return 
    
    deputados_completos = []

    for deputado in deputados_base:        
        uri_detalhes = deputado.get('uri')
        if not uri_detalhes:
            print(f"{deputado.get(id)} - URI não encontrada para este deputado. Pulando.")
            continue
        
        detalhes_json = buscar_detalhes_deputado_xml(uri_detalhes)
        
        if detalhes_json:
            deputado_combinado = {
                "id_dados_abertos": deputado.get('id'),
                "nome_civil": detalhes_json.get('nome_civil'),
                "nome_eleitoral": detalhes_json.get('nome_eleitoral'),
                "sigla_partido": deputado.get('siglaPartido'),
                "id_partido": ###
                "sigla_uf": 
                "email": deputado.get('email'),
                **detalhes_json  # Adiciona todos os itens do dicionário de detalhes
            }
            deputados_completos.append(deputado_combinado)

    print(json.dumps(deputados_completos, indent=2, ensure_ascii=False))

# id (DB)
# id_dados_abertos
# nome_civil (no xml)
# nome_eleitoral(xml)
# sigla_partido
# id_partido
# sigla_uf
# id_legislativo
# url_foto
# sexo (no xml)
# gabinete


# {
#     "id": 220593,
#     "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/220593",
#     "nome": "Abilio Brunini",
#     "siglaPartido": "PL",
#     "uriPartido": "https://dadosabertos.camara.leg.br/api/v2/partidos/37906",
#     "siglaUf": "MT",
#     "idLegislatura": 57,
#     "urlFoto": "https://www.camara.leg.br/internet/deputado/bandep/220593.jpg",
#     "email": null
# }

# nome_civil
# nome_eleitoral
# sexo

# <xml>
#   <dados>
#     <id>220593</id>
#     <uri>https://dadosabertos.camara.leg.br/api/v2/deputados/220593</uri>
#     <nomeCivil>ABILIO JACQUES BRUNINI MOUMER</nomeCivil>
#     <ultimoStatus>
#       <id>220593</id>
#       <uri>https://dadosabertos.camara.leg.br/api/v2/deputados/220593</uri>
#       <nome>Abilio Brunini</nome>
#       <siglaPartido>PL</siglaPartido>
#       <uriPartido/>
#       <siglaUf>MT</siglaUf>
#       <idLegislatura>57</idLegislatura>
#       <urlFoto>https://www.camara.leg.br/internet/deputado/bandep/220593.jpg</urlFoto>
#       <email/>
#       <data>2025-01-01</data>
#       <nomeEleitoral>Abilio Brunini</nomeEleitoral>
#       <gabinete>
#         <nome/>
#         <predio/>
#         <sala/>
#         <andar/>
#         <telefone/>
#         <email/>
#       </gabinete>
#       <situacao>Vacância</situacao>
#       <condicaoEleitoral>Titular</condicaoEleitoral>
#       <descricaoStatus/>
#     </ultimoStatus>
#     <cpf>99770962104</cpf>
#     <sexo>M</sexo>
#     <urlWebsite/>
#     <redeSocial/>
#     <dataNascimento>1984-01-31</dataNascimento>
#     <dataFalecimento/>
#     <ufNascimento>MT</ufNascimento>
#     <municipioNascimento>Cuiabá</municipioNascimento>
#     <escolaridade>Superior</escolaridade>
#   </dados>
#   <links>
#     <link>
#       <rel>self</rel>
#       <href>https://dadosabertos.camara.leg.br/api/v2/deputados/220593</href>
#     </link>
#   </links>
# </xml>


main()