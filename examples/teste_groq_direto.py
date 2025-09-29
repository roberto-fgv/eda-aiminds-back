"""Teste específico da API Groq para diagnosticar o erro 400."""
import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import requests
import json
from src.settings import GROQ_API_KEY

def test_groq_direct():
    """Testa API Groq diretamente."""
    
    print("🧪 TESTE DIRETO API GROQ")
    print("=" * 40)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY não encontrada")
        return
        
    print(f"🔑 API Key: {GROQ_API_KEY[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Listar modelos
    print("\n1️⃣ Testando endpoint de modelos...")
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Modelos disponíveis:")
            for model in models.get("data", []):
                print(f"  • {model.get('id')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Teste 2: Chat completion simples
    print("\n2️⃣ Testando chat completion...")
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": "Diga apenas 'OK'"}
        ],
        "temperature": 0.1,
        "max_tokens": 5,
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            print(f"✅ Resposta: {message}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Teste 3: Verificar diferentes modelos
    print("\n3️⃣ Testando modelos alternativos...")
    
    models_to_test = [
        "llama3-8b-8192",
        "mixtral-8x7b-32768", 
        "llama-3.1-70b-versatile"
    ]
    
    for model in models_to_test:
        payload["model"] = model
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ {model}: OK")
            else:
                print(f"❌ {model}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model}: {str(e)[:50]}")

if __name__ == "__main__":
    test_groq_direct()