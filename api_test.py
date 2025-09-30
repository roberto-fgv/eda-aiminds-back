"""API Simplificada para Teste de Integração"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Criar app FastAPI
app = FastAPI(title="EDA AI Minds API - Teste", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz - Status básico da API"""
    return {
        "status": "ok",
        "message": "EDA AI Minds Backend API - Teste Simplificado",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Endpoint de saúde"""
    return {
        "status": "healthy",
        "service": "eda-aiminds-backend",
        "timestamp": "2025-09-29"
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {
        "test": "success",
        "message": "API está funcionando corretamente!",
        "integration": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)