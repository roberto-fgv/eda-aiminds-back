"""Script de teste para múltiplos provedores LLM (Google Gemini vs xAI Grok).

Este script testa a nova arquitetura genérica de LLM, comparando
diferentes provedores e validando funcionalidades.
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH  
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import time
from src.agent.generic_llm_agent import GenericLLMAgent
from src.llm.manager import llm_manager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def test_provider_basic(agent: GenericLLMAgent, provider_name: str) -> dict:
    """Teste básico de um provedor."""
    print(f"\n🧪 TESTANDO PROVEDOR: {provider_name.upper()}")
    print("=" * 60)
    
    test_query = "Explique em 2 parágrafos o que é machine learning."
    
    print(f"❓ Query: '{test_query}'")
    
    start_time = time.time()
    response = agent.process(test_query)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    success = response.get("success", False)
    content = response.get("content", "")
    metadata = response.get("metadata", {})
    
    print(f"⏱️  Tempo: {processing_time:.2f}s")
    print(f"✅ Sucesso: {success}")
    print(f"🤖 Provider: {metadata.get('provider', 'N/A')}")
    print(f"🧠 Modelo: {metadata.get('model', 'N/A')}")
    print(f"💾 Cache: {metadata.get('cache_used', False)}")
    print(f"📝 Resposta: {len(content)} caracteres")
    
    if success and len(content) > 50:
        print(f"📄 Preview: {content[:100]}...")
        return {
            "success": True,
            "processing_time": processing_time,
            "content_length": len(content),
            "provider": metadata.get('provider'),
            "model": metadata.get('model')
        }
    else:
        print(f"❌ Erro: {content}")
        return {
            "success": False,
            "error": content,
            "processing_time": processing_time
        }


def test_provider_switch(agent: GenericLLMAgent) -> dict:
    """Testa troca dinâmica de provedor."""
    print(f"\n🔄 TESTE DE TROCA DE PROVEDOR")
    print("=" * 60)
    
    # Listar provedores disponíveis
    available = agent.list_available_providers()
    print("📋 Provedores disponíveis:")
    for provider_type, info in available.items():
        status = "✅" if info["api_key_available"] else "❌"
        print(f"  {status} {info['name']} ({provider_type})")
        print(f"      Modelos: {', '.join(info['models'])}")
    
    # Testar troca se houver múltiplos provedores
    available_with_keys = [p for p, info in available.items() if info["api_key_available"]]
    
    if len(available_with_keys) >= 2:
        current_info = agent.get_provider_info()
        current_provider = current_info["provider"]
        
        # Encontrar outro provedor
        other_provider = None
        for provider_type in available_with_keys:
            if provider_type != current_provider:
                other_provider = provider_type
                break
        
        if other_provider:
            print(f"\n🔄 Trocando de {current_provider} para {other_provider}")
            
            switch_success = agent.switch_provider(other_provider)
            
            if switch_success:
                new_info = agent.get_provider_info()
                print(f"✅ Troca realizada: {new_info['provider']} ({new_info['model']})")
                
                # Teste rápido no novo provedor
                test_response = agent.process("Diga apenas 'OK' para confirmar funcionamento.")
                if test_response.get("success"):
                    print("✅ Novo provedor funcionando")
                    return {"switch_success": True, "new_provider": new_info["provider"]}
                else:
                    print("❌ Novo provedor não funcionou")
                    return {"switch_success": False, "error": "Teste falhou"}
            else:
                print("❌ Falha na troca de provedor")
                return {"switch_success": False, "error": "Switch failed"}
        else:
            print("⚠️  Apenas um provedor disponível, não é possível trocar")
            return {"switch_success": False, "error": "Only one provider available"}
    else:
        print("⚠️  Menos de 2 provedores disponíveis")
        return {"switch_success": False, "error": "Insufficient providers"}


def test_fraud_analysis() -> dict:
    """Teste de análise de fraude."""
    print(f"\n🕵️  TESTE ANÁLISE DE FRAUDE")
    print("=" * 60)
    
    # Dados simulados de fraude
    fraud_data = {
        "total_transactions": 10000,
        "fraud_count": 150,
        "fraud_percentage": 1.5,
        "high_risk_patterns": [
            {"pattern": "high_amount_night", "count": 45},
            {"pattern": "multiple_locations", "count": 38},
            {"pattern": "new_merchant", "count": 67}
        ],
        "avg_fraud_amount": 2847.50,
        "avg_normal_amount": 127.30
    }
    
    # Testar com Google Gemini
    try:
        agent = GenericLLMAgent(name="fraud_analyzer", provider_type="google_gemini")
        
        start_time = time.time()
        response = agent.analyze_fraud_data(fraud_data)
        end_time = time.time()
        
        success = response.get("success", False)
        content = response.get("content", "")
        
        print(f"⏱️  Tempo: {end_time - start_time:.2f}s")
        print(f"✅ Sucesso: {success}")
        print(f"📝 Análise: {len(content)} caracteres")
        
        if success:
            print(f"📄 Preview: {content[:200]}...")
            return {"success": True, "analysis_length": len(content)}
        else:
            print(f"❌ Erro: {content}")
            return {"success": False, "error": content}
            
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Função principal de teste."""
    print("🚀 TESTE SISTEMA LLM GENÉRICO")
    print("=" * 60)
    
    results = {
        "providers_tested": [],
        "switch_test": {},
        "fraud_analysis": {}
    }
    
    # Listar provedores disponíveis
    available_providers = llm_manager.get_available_providers()
    
    print("📋 Status dos provedores:")
    for provider_type, info in available_providers.items():
        status = "🟢 Disponível" if info["api_key_available"] else "🔴 API Key ausente"
        print(f"  • {info['name']}: {status}")
    
    # Testar cada provedor disponível
    for provider_type, info in available_providers.items():
        if info["api_key_available"]:
            try:
                agent = GenericLLMAgent(
                    name=f"test_{provider_type}",
                    provider_type=provider_type
                )
                
                test_result = test_provider_basic(agent, info["name"])
                test_result["provider_type"] = provider_type
                results["providers_tested"].append(test_result)
                
            except Exception as e:
                print(f"❌ Erro ao testar {provider_type}: {e}")
                results["providers_tested"].append({
                    "provider_type": provider_type,
                    "success": False,
                    "error": str(e)
                })
    
    # Teste de troca de provedor
    if len([p for p, info in available_providers.items() if info["api_key_available"]]) > 0:
        try:
            agent = GenericLLMAgent()
            results["switch_test"] = test_provider_switch(agent)
        except Exception as e:
            print(f"❌ Erro no teste de troca: {e}")
            results["switch_test"] = {"error": str(e)}
    
    # Teste de análise de fraude
    results["fraud_analysis"] = test_fraud_analysis()
    
    # Resumo final
    print(f"\n🏁 RESUMO DOS TESTES")
    print("=" * 60)
    
    successful_providers = [r for r in results["providers_tested"] if r.get("success", False)]
    
    print(f"✅ Provedores funcionando: {len(successful_providers)}/{len(results['providers_tested'])}")
    for provider in successful_providers:
        print(f"  • {provider['provider_type']}: {provider['processing_time']:.2f}s")
    
    if results["switch_test"].get("switch_success"):
        print(f"✅ Troca de provedor: Funcionando")
    else:
        print(f"⚠️  Troca de provedor: {results['switch_test'].get('error', 'N/A')}")
    
    if results["fraud_analysis"].get("success"):
        print(f"✅ Análise de fraude: Funcionando")
    else:
        print(f"❌ Análise de fraude: {results['fraud_analysis'].get('error', 'Falhou')}")
    
    # Status final
    if len(successful_providers) > 0:
        print(f"\n🎉 SISTEMA LLM GENÉRICO FUNCIONANDO!")
        print(f"   {len(successful_providers)} provedor(es) disponível(eis)")
    else:
        print(f"\n❌ NENHUM PROVEDOR FUNCIONANDO")
        print("   Verifique as API keys nas configurações")


if __name__ == "__main__":
    main()