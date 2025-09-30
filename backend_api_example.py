# API REST para integração Frontend <-> Backend EDA AI Minds
# Este arquivo é um exemplo de como estruturar a API no backend Python
# Adicione este código ao seu projeto backend Python

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
import os
import time
from datetime import datetime

# Importar seus agentes do projeto
from src.agent.orchestrator_agent import OrchestratorAgent
from src.data.data_processor import DataProcessor, load_csv_file, create_demo_data

app = FastAPI(title="EDA AI Minds API", version="1.0.0")

# Configurar CORS para permitir requests do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # URLs do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models para requests/responses
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AnalysisRequest(BaseModel):
    analysis_type: str
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class LoadDataRequest(BaseModel):
    source: str  # 'url', 'base64', 'demo'
    data: Any
    session_id: Optional[str] = None

class DemoDataRequest(BaseModel):
    data_type: str  # 'fraud_detection', 'sales', 'customer'
    num_rows: int = 1000
    session_id: Optional[str] = None

# Armazenar sessões em memória (em produção, usar Redis ou banco de dados)
sessions: Dict[str, Dict] = {}

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Cria ou recupera uma sessão"""
    if session_id and session_id in sessions:
        return session_id
    
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = {
        "created_at": datetime.now(),
        "orchestrator": None,
        "data_processor": None,
        "conversation_history": []
    }
    return new_session_id

def get_orchestrator(session_id: str) -> OrchestratorAgent:
    """Obtém ou cria um agente orquestrador para a sessão"""
    if sessions[session_id]["orchestrator"] is None:
        sessions[session_id]["orchestrator"] = OrchestratorAgent(
            enable_csv_agent=True,
            enable_rag_agent=True,
            enable_data_processor=True
        )
    return sessions[session_id]["orchestrator"]

@app.get("/")
async def root():
    """Endpoint raiz - Status básico da API"""
    return {
        "status": "ok",
        "message": "EDA AI Minds Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "active_sessions": len(sessions)
    }

@app.get("/api/status")
async def get_status():
    """Status do sistema e agentes disponíveis"""
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
    """Upload e processamento de arquivo"""
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
        
        # Salvar arquivo temporariamente
        temp_path = f"temp/{session_id}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Processar arquivo com DataProcessor
        processor = load_csv_file(temp_path)
        sessions[session_id]["data_processor"] = processor
        
        # Obter informações do arquivo
        df = processor.data
        quality_report = processor.get_data_quality_report()
        
        # Limpar arquivo temporário
        os.remove(temp_path)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": f"Arquivo {file.filename} processado com sucesso",
            "session_id": session_id,
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "rows": len(df),
                "columns": len(df.columns),
                "quality_score": quality_report.get("overall_score", 0)
            },
            "metadata": {
                "processing_time": processing_time
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_orchestrator(request: ChatRequest):
    """Enviar mensagem para o agente orquestrador"""
    start_time = time.time()
    
    try:
        # Verificar se sessão existe
        if not request.session_id or request.session_id not in sessions:
            raise HTTPException(status_code=400, detail="Sessão não encontrada")
        
        # Obter orquestrador
        orchestrator = get_orchestrator(request.session_id)
        
        # Processar mensagem
        result = orchestrator.process(request.message, request.context or {})
        
        # Salvar no histórico
        sessions[request.session_id]["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": request.message,
            "agent_response": result
        })
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "response": result.get("content", ""),
            "agent_type": result.get("agent_type", "orchestrator"),
            "query_type": result.get("query_type", "general"),
            "context": result.get("context", {}),
            "metadata": {
                "processing_time": processing_time,
                "confidence": result.get("confidence", 0.8),
                "suggestions": result.get("suggestions", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Análise específica dos dados"""
    start_time = time.time()
    
    try:
        if not request.session_id or request.session_id not in sessions:
            raise HTTPException(status_code=400, detail="Sessão não encontrada")
        
        processor = sessions[request.session_id]["data_processor"]
        if not processor:
            raise HTTPException(status_code=400, detail="Nenhum arquivo carregado")
        
        # Executar análise baseada no tipo
        if request.analysis_type == "quick":
            results = processor.quick_analysis()
        elif request.analysis_type == "quality":
            results = processor.get_data_quality_report()
        elif request.analysis_type == "custom":
            # Análise customizada com parâmetros
            results = processor.analyze(request.parameters.get("query", ""))
        else:
            raise HTTPException(status_code=400, detail="Tipo de análise não suportado")
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "analysis": {
                "summary": results.get("summary", ""),
                "insights": results.get("insights", []),
                "visualizations": results.get("visualizations", []),
                "code": results.get("code", ""),
                "tables": results.get("tables", [])
            },
            "metadata": {
                "processing_time": processing_time,
                "data_quality": results.get("quality_score", 0),
                "recommendations": results.get("recommendations", [])
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
        
        # Gerar dados baseado no tipo
        processor = create_demo_data(
            request.data_type, 
            num_rows=request.num_rows
        )
        
        sessions[session_id]["data_processor"] = processor
        
        # Obter informações dos dados gerados
        df = processor.data
        quality_report = processor.get_data_quality_report()
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": f"Dados de {request.data_type} gerados com sucesso",
            "session_id": session_id,
            "file_info": {
                "filename": f"{request.data_type}_demo.csv",
                "size": len(df) * len(df.columns) * 8,  # Estimativa
                "rows": len(df),
                "columns": len(df.columns),
                "quality_score": quality_report.get("overall_score", 95)
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
    """Obter histórico de conversação"""
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
    """Limpar dados da sessão"""
    if session_id in sessions:
        del sessions[session_id]
    
    return {
        "success": True,
        "message": "Sessão limpa com sucesso"
    }

@app.get("/api/data-quality/{session_id}")
async def get_data_quality(session_id: str):
    """Obter relatório de qualidade dos dados"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    processor = sessions[session_id]["data_processor"]
    if not processor:
        raise HTTPException(status_code=400, detail="Nenhum arquivo carregado")
    
    quality_report = processor.get_data_quality_report()
    suggestions = processor.suggest_improvements()
    
    return {
        "success": True,
        "data": {
            "quality_report": quality_report,
            "suggestions": suggestions
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)