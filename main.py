from fastapi import FastAPI
from routers.deputado_router import deputado_router
from routers.analise_router import analise_router
from routers.despesa_router import despesa_router
from routers.proposicao_router import proposicao_router
from routers.sessao_votacao_router import sessaovotacao_router
from routers.voto_individual_router import voto_router
from routers.ranking_deputados_router import deputado_atuantes_router


app = FastAPI()

# Incluindo as rotas
app.include_router(deputado_router)
app.include_router(despesa_router)
app.include_router(analise_router)
app.include_router(proposicao_router)
app.include_router(sessaovotacao_router)
app.include_router(voto_router)
app.include_router(deputado_atuantes_router)
