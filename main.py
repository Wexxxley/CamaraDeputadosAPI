from fastapi import FastAPI
from routers.deputado_router import deputado_router

app = FastAPI()

# Incluindo as rotas
app.include_router(deputado_router)