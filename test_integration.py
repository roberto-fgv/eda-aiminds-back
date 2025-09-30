#!/usr/bin/env python3
"""
Teste de Integração - EDA AI Minds Backend
Script para validar que todos os componentes estão funcionando corretamente
"""

import sys
import time
from datetime import datetime

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("🧪 TESTANDO IMPORTS...")
    
    try:
        # Core dependencies
        import pandas as pd
        import numpy as np
        print("✅ Pandas/Numpy: OK")
        
        # FastAPI
        import fastapi
        import uvicorn
        print("✅ FastAPI/Uvicorn: OK")
        
        # Projeto - Agentes
        from src.agent.orchestrator_agent import OrchestratorAgent
        print("✅ OrchestratorAgent: OK")
        
        from src.data.data_processor import DataProcessor
        print("✅ DataProcessor: OK")
        
        # Projeto - LLM System
        from src.agent.generic_llm_agent import GenericLLMAgent
        from src.llm.manager import LLMProviderFactory
        print("✅ Sistema LLM Genérico: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_agents():
    """Testa se os agentes podem ser inicializados"""
    print("\n🤖 TESTANDO AGENTES...")
    
    try:
        # Re-import após teste anterior
        from src.agent.orchestrator_agent import OrchestratorAgent
        from src.agent.generic_llm_agent import GenericLLMAgent
        
        # Teste Orchestrator
        orchestrator = OrchestratorAgent(
            enable_csv_agent=True,
            enable_rag_agent=True, 
            enable_data_processor=True
        )
        print("✅ OrchestratorAgent: Inicializado")
        
        # Teste GenericLLMAgent
        llm_agent = GenericLLMAgent(name="test_agent")
        print("✅ GenericLLMAgent: Inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização dos agentes: {e}")
        return False

def test_data_processing():
    """Testa o sistema de processamento de dados"""
    print("\n📊 TESTANDO PROCESSAMENTO DE DADOS...")
    
    try:
        from src.data.data_processor import create_demo_data, DataProcessor
        
        # Criar dados demo
        demo_data = create_demo_data("fraud_detection", 100)
        print(f"✅ Dados demo criados: {len(demo_data)} linhas")
        
        # Teste DataProcessor
        processor = DataProcessor()
        analysis = processor.analyze_dataframe(demo_data)
        if analysis is not None:
            print(f"✅ Análise concluída: {type(analysis).__name__} gerado")
        else:
            print("⚠️  Análise retornou None (normal em modo básico)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def test_llm_providers():
    """Testa os provedores LLM disponíveis"""
    print("\n🧠 TESTANDO PROVEDORES LLM...")
    
    try:
        from src.llm.manager import LLMProviderFactory
        from src.llm.base import LLMProvider
        
        # Listar provedores disponíveis
        available = LLMProviderFactory.get_available_providers()
        available_names = [provider.value for provider in available]
        print(f"✅ Provedores disponíveis: {', '.join(available_names)}")
        
        # Testar criação de provider (sem fazer chamada real)
        if LLMProvider.GOOGLE_GEMINI in available:
            provider = LLMProviderFactory.create_provider(LLMProvider.GOOGLE_GEMINI)
            print("✅ Google Gemini provider: Criado")
            
        if LLMProvider.GROQ in available:
            provider = LLMProviderFactory.create_provider(LLMProvider.GROQ)
            print("✅ Groq provider: Criado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos provedores LLM: {e}")
        return False

def test_api_file():
    """Testa se o arquivo da API pode ser importado"""
    print("\n🔌 TESTANDO ARQUIVO DA API...")
    
    try:
        import backend_api_example
        print("✅ backend_api_example: Importado com sucesso")
        
        # Verificar se app existe
        app = getattr(backend_api_example, 'app', None)
        if app:
            print("✅ FastAPI app: Encontrada")
        else:
            print("❌ FastAPI app: Não encontrada")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def main():
    """Executa todos os testes de integração"""
    print("=" * 60)
    print("🚀 TESTE DE INTEGRAÇÃO - EDA AI MINDS BACKEND")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Agentes", test_agents), 
        ("Processamento de Dados", test_data_processing),
        ("Provedores LLM", test_llm_providers),
        ("Arquivo da API", test_api_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ FALHA CRÍTICA em {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 RESULTADO FINAL: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 INTEGRAÇÃO COMPLETA! Sistema pronto para uso!")
        print("📝 Para iniciar a API: uvicorn backend_api_example:app --reload")
        print("📖 Documentação: http://localhost:8000/docs")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        
    print("=" * 60)
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)