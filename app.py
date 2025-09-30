from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
import os
import time
from datetime import datetime

app = FastAPI(title="EDA AI Minds API", version="1.0.0")

# Configurar CORS para permitir requests do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://localhost:8081", 
        "http://localhost:3000", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models para requests/responses
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DemoDataRequest(BaseModel):
    data_type: str  # 'fraud_detection', 'sales', 'customer'
    num_rows: int = 1000
    session_id: Optional[str] = None

# Armazenar sessões em memória
sessions: Dict[str, Dict] = {}

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Cria ou recupera uma sessão"""
    if session_id and session_id in sessions:
        return session_id
    
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = {
        "created_at": datetime.now(),
        "conversation_history": [],
        "has_data": False
    }
    return new_session_id

@app.get("/api/status")
async def get_status():
    """Status do sistema"""
    return {
        "success": True,
        "message": "Sistema EDA AI Minds ativo",
        "data": {
            "active_sessions": len(sessions),
            "available_agents": ["orchestrator", "csv_analysis", "rag"],
            "supported_formats": [".csv", ".xlsx", ".json"],
            "max_file_size": "50MB"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """Upload e processamento de arquivo (simulado)"""
    start_time = time.time()
    
    try:
        # Validar tipo de arquivo
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(
                status_code=400, 
                detail="Formato não suportado. Use CSV, XLSX ou JSON."
            )
        
        # Criar ou recuperar sessão
        session_id = get_or_create_session(session_id)
        
        # Simular processamento do arquivo
        content = await file.read()
        sessions[session_id]["has_data"] = True
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": f"Arquivo {file.filename} processado com sucesso",
            "session_id": session_id,
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "rows": 1500,  # Simulado
                "columns": 12,  # Simulado
                "quality_score": 85  # Simulado
            },
            "metadata": {
                "processing_time": processing_time
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_orchestrator(request: ChatRequest):
    """Chat simulado com o agente"""
    start_time = time.time()
    
    try:
        # Verificar se sessão existe
        if not request.session_id or request.session_id not in sessions:
            raise HTTPException(status_code=400, detail="Sessão não encontrada")
        
        # Simular resposta baseada na mensagem
        message = request.message.lower()
        
        if "gráfico" in message or "chart" in message:
            response_text = "📊 Analisando dados para gerar gráficos...\n\nEncontrei correlações interessantes entre as variáveis. Recomendo:\n• Gráfico de dispersão para vendas vs tempo\n• Histograma da distribuição de preços\n• Boxplot para identificar outliers"
            response_type = "chart"
        elif "código" in message or "python" in message:
            response_text = """import pandas as pd
import matplotlib.pyplot as plt

# Carregando os dados
df = pd.read_csv('dados.csv')
print(df.describe())

# Gráfico simples
plt.figure(figsize=(10, 6))
df.hist()
plt.show()"""
            response_type = "code"
        elif "tabela" in message or "dados" in message:
            response_text = "📋 Resumo dos dados:\n• 1.500 registros processados\n• 12 colunas identificadas\n• 3 variáveis numéricas\n• 2 variáveis categóricas\n• Score de qualidade: 85/100"
            response_type = "table"
        else:
            response_text = f"Entendi sua pergunta: '{request.message}'\n\n🤖 Estou processando com os agentes multiagentes do EDA AI Minds!\n\nPosso ajudar com:\n🔍 Análise exploratória\n📊 Gráficos e visualizações\n🐍 Código Python\n📋 Relatórios detalhados"
            response_type = "text"
        
        # Salvar no histórico
        sessions[request.session_id]["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": request.message,
            "agent_response": response_text
        })
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "response": response_text,
            "agent_type": "orchestrator",
            "query_type": response_type,
            "context": {},
            "metadata": {
                "processing_time": processing_time,
                "confidence": 0.9,
                "suggestions": ["Tente perguntar sobre gráficos", "Solicite código Python", "Peça análise dos dados"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo-data")
async def generate_demo_data(request: DemoDataRequest):
    """Gerar dados de demonstração"""
    start_time = time.time()
    
    try:
        session_id = get_or_create_session(request.session_id)
        
        # Simular geração de dados
        sessions[session_id]["has_data"] = True
        
        data_info = {
            "fraud_detection": {"rows": request.num_rows, "columns": 15, "quality": 92},
            "sales": {"rows": request.num_rows, "columns": 8, "quality": 88},
            "customer": {"rows": request.num_rows, "columns": 12, "quality": 90}
        }
        
        info = data_info.get(request.data_type, data_info["sales"])
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": f"Dados de {request.data_type} gerados com sucesso",
            "session_id": session_id,
            "file_info": {
                "filename": f"{request.data_type}_demo.csv",
                "size": info["rows"] * info["columns"] * 8,
                "rows": info["rows"],
                "columns": info["columns"],
                "quality_score": info["quality"]
            },
            "metadata": {
                "processing_time": processing_time,
                "data_type": request.data_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Obter histórico"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "created_at": sessions[session_id]["created_at"].isoformat(),
            "conversation_history": sessions[session_id]["conversation_history"]
        }
    }

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Limpar sessão"""
    if session_id in sessions:
        del sessions[session_id]
    
    return {
        "success": True,
        "message": "Sessão limpa com sucesso"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando EDA AI Minds Backend...")
    print("📡 API disponível em: http://localhost:8000")
    print("📋 Documentação em: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)