from fastapi import FastAPI
from routers.deputado_router import deputado_router
from routers.analise_router import analise_router
from routers.despesa_router import despesa_router

app = FastAPI()

# Incluindo as rotas
app.include_router(deputado_router)
app.include_router(despesa_router)
app.include_router(analise_router)
