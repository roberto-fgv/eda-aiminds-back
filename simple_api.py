"""API Mínima Funcional para Teste"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="EDA AI Minds API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API funcionando!", "status": "ok"}

@app.get("/test")
def test():
    return {"test": "success", "integration": "ready"}

if __name__ == "__main__":
    print("🚀 Iniciando API na porta 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")