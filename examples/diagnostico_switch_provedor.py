"""Script de diagnóstico para problemas de troca de provedor LLM.

Este script testa especificamente a funcionalidade de switch entre provedores
e identifica onde está o problema.
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH  
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.agent.generic_llm_agent import GenericLLMAgent
from src.llm.manager import llm_manager
from src.llm.base import LLMRequest
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def test_api_key_format():
    """Testa formato das API keys."""
    print("🔍 DIAGNÓSTICO DE API KEYS")
    print("=" * 50)
    
    from src.settings import GOOGLE_API_KEY, XAI_API_KEY
    
    # Testar Google API Key
    if GOOGLE_API_KEY:
        if GOOGLE_API_KEY.startswith("AIza"):
            print("✅ Google API Key: Formato correto")
        else:
            print(f"❌ Google API Key: Formato suspeito - {GOOGLE_API_KEY[:10]}...")
    else:
        print("❌ Google API Key: Ausente")
    
    # Testar xAI API Key
    if XAI_API_KEY:
        if XAI_API_KEY.startswith("xai-"):
            print("✅ xAI API Key: Formato correto")
        elif XAI_API_KEY.startswith("gsk_"):
            print("❌ xAI API Key: ERRO - Esta é uma chave do Groq, não xAI!")
            print("   Você precisa de uma chave de https://console.x.ai/")
        else:
            print(f"❌ xAI API Key: Formato suspeito - {XAI_API_KEY[:10]}...")
    else:
        print("❌ xAI API Key: Ausente")


def test_provider_creation():
    """Testa criação individual de cada provedor."""
    print("\n🏗️  DIAGNÓSTICO DE CRIAÇÃO DE PROVEDORES")
    print("=" * 50)
    
    # Testar Google
    try:
        google_provider = llm_manager.create_provider("google_gemini")
        print("✅ Google Gemini: Criado com sucesso")
        
        # Teste rápido
        test_req = LLMRequest(prompt="Diga apenas 'OK'", temperature=0.1, max_tokens=5)
        response = google_provider.generate(test_req)
        
        if response.success:
            print("✅ Google Gemini: Teste de API passou")
        else:
            print(f"❌ Google Gemini: Teste falhou - {response.error_message}")
            
    except Exception as e:
        print(f"❌ Google Gemini: Erro na criação - {e}")
    
    # Testar xAI Grok
    try:
        grok_provider = llm_manager.create_provider("xai_grok")
        print("✅ xAI Grok: Criado com sucesso")
        
        # Teste rápido
        test_req = LLMRequest(prompt="Diga apenas 'OK'", temperature=0.1, max_tokens=5)
        response = grok_provider.generate(test_req)
        
        if response.success:
            print("✅ xAI Grok: Teste de API passou")
        else:
            print(f"❌ xAI Grok: Teste falhou - {response.error_message}")
            
    except Exception as e:
        print(f"❌ xAI Grok: Erro na criação - {e}")


def test_agent_switch():
    """Testa switch no agente especificamente."""
    print("\n🔄 DIAGNÓSTICO DE TROCA DE PROVEDOR")
    print("=" * 50)
    
    try:
        # Criar agente com Google
        agent = GenericLLMAgent(name="test_switch", provider_type="google_gemini")
        initial_info = agent.get_provider_info()
        print(f"✅ Agente inicial: {initial_info['provider']} ({initial_info['model']})")
        
        # Verificar provedores disponíveis
        available = agent.list_available_providers()
        grok_available = available.get("xai_grok", {}).get("api_key_available", False)
        
        if not grok_available:
            print("❌ Switch impossível: xAI Grok não disponível (API key)")
            return
        
        print("✅ xAI Grok disponível, tentando switch...")
        
        # Tentar switch
        switch_result = agent.switch_provider("xai_grok", "grok-beta")
        
        if switch_result:
            new_info = agent.get_provider_info()
            print(f"✅ Switch realizado: {new_info['provider']} ({new_info['model']})")
            
            # Teste no novo provedor
            test_response = agent.process("Responda apenas 'OK' para confirmar.")
            if test_response.get("success"):
                print("✅ Novo provedor funcionando!")
            else:
                print(f"❌ Novo provedor não funciona: {test_response.get('content', '')}")
        else:
            print("❌ Switch falhou")
            
    except Exception as e:
        print(f"❌ Erro no teste de switch: {e}")


def test_grok_direct_api():
    """Testa API do Grok diretamente."""
    print("\n🌐 TESTE DIRETO API GROK")
    print("=" * 50)
    
    try:
        import requests
        from src.settings import XAI_API_KEY
        
        if not XAI_API_KEY:
            print("❌ XAI_API_KEY não configurada")
            return
            
        # Testar endpoint de modelos primeiro
        headers = {
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print("🔍 Testando endpoint de modelos...")
        models_url = "https://api.x.ai/v1/models"
        
        try:
            response = requests.get(models_url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                models = response.json()
                print("✅ API conectou com sucesso!")
                print("📋 Modelos disponíveis:")
                for model in models.get("data", []):
                    print(f"  • {model.get('id', 'Unknown')}")
            else:
                print(f"❌ API retornou erro: {response.status_code}")
                print(f"Resposta: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            
    except ImportError:
        print("❌ Biblioteca requests não disponível")
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")


def main():
    """Função principal de diagnóstico."""
    print("🩺 DIAGNÓSTICO COMPLETO - TROCA DE PROVEDOR LLM")
    print("=" * 60)
    
    # Executar todos os testes
    test_api_key_format()
    test_provider_creation()
    test_agent_switch()
    test_grok_direct_api()
    
    print("\n🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)
    print("📝 Se o xAI Grok falhou:")
    print("   1. Verifique se a API key é realmente do xAI (deve começar com 'xai-')")
    print("   2. Acesse https://console.x.ai/ para gerar uma nova chave") 
    print("   3. xAI pode estar em manutenção ou com rate limit")
    print("\n📝 Se tudo passou mas switch falha:")
    print("   1. Pode ser um bug na lógica de switch")
    print("   2. Verifique logs detalhados do agente")


if __name__ == "__main__":
    main()