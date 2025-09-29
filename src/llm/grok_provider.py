"""Provedor xAI Grok para o sistema LLM genérico."""
import requests
import json
from typing import Dict, Any, Optional

from src.llm.base import (
    BaseLLMProvider, 
    LLMProvider, 
    LLMRequest, 
    LLMResponse,
    LLMConfig,
    LLMProviderFactory
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GrokProvider(BaseLLMProvider):
    """Provedor para xAI Grok API."""
    
    def __init__(self, config: LLMConfig):
        """Inicializa provedor Grok."""
        super().__init__(config)
        self.logger = logger
        self.base_url = config.base_url or "https://api.x.ai/v1"
        
    def _initialize_client(self) -> None:
        """Inicializa cliente Grok (baseado em requests)."""
        try:
            # Grok usa REST API, não precisa de cliente específico
            self._client = {
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                "base_url": self.base_url
            }
            self.logger.info(f"xAI Grok inicializado: {self.model}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Grok: {e}")
            raise
    
    def _call_api(self, request: LLMRequest) -> LLMResponse:
        """Chama xAI Grok API."""
        try:
            # Preparar mensagens no formato OpenAI-compatible
            messages = []
            
            # Adicionar system prompt se fornecido
            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })
            
            # Preparar prompt do usuário
            user_content = request.prompt
            if request.context:
                # Formatar contexto de forma estruturada
                context_str = self._format_context(request.context)
                user_content = f"Contexto:\n{context_str}\n\nConsulta: {request.prompt}"
            
            messages.append({
                "role": "user", 
                "content": user_content
            })
            
            # Preparar payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False
            }
            
            # Fazer request
            url = f"{self._client['base_url']}/chat/completions"
            response = requests.post(
                url,
                headers=self._client["headers"],
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extrair resposta
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                
                # Extrair informações de uso
                usage = data.get("usage", {})
                
                return LLMResponse(
                    content=content,
                    provider=LLMProvider.XAI_GROK,
                    model=self.model,
                    success=True,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                )
            else:
                raise Exception("Resposta inválida da API Grok")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de rede na API Grok: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.XAI_GROK,
                model=self.model,
                success=False,
                error_message=f"Erro de rede: {str(e)}"
            )
            
        except Exception as e:
            self.logger.error(f"Erro na API Grok: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.XAI_GROK,
                model=self.model,
                success=False,
                error_message=str(e)
            )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formata contexto de forma estruturada para Grok."""
        formatted_parts = []
        
        if "file_path" in context:
            formatted_parts.append(f"Arquivo: {context['file_path']}")
        
        if "data_info" in context:
            data_info = context["data_info"]
            formatted_parts.append(
                f"Dimensões: {data_info.get('rows', 'N/A')} linhas × {data_info.get('columns', 'N/A')} colunas"
            )
        
        if "fraud_data" in context:
            fraud_info = context["fraud_data"]
            formatted_parts.append(
                f"Fraudes detectadas: {fraud_info.get('count', 0)} de {fraud_info.get('total', 0)} transações"
            )
        
        # Adicionar qualquer outro contexto como JSON
        other_context = {k: v for k, v in context.items() 
                        if k not in ["file_path", "data_info", "fraud_data"]}
        
        if other_context:
            formatted_parts.append(f"Dados adicionais: {json.dumps(other_context, ensure_ascii=False)}")
        
        return "\n".join(formatted_parts)
    
    def validate_config(self) -> bool:
        """Valida configuração específica do Grok."""
        if not super().validate_config():
            return False
            
        # Verificar se modelo é suportado
        supported_models = [
            "grok-beta", "grok-2-1212", "grok-2-vision-1212", 
            "grok-2-public-beta", "grok-vision-beta"
        ]
        
        return self.model in supported_models
    
    def test_connection(self) -> bool:
        """Testa conexão com a API Grok."""
        try:
            test_request = LLMRequest(
                prompt="Teste de conexão. Responda apenas 'OK'.",
                temperature=0.1,
                max_tokens=10
            )
            
            response = self.generate(test_request)
            return response.success and "ok" in response.content.lower()
            
        except Exception as e:
            self.logger.error(f"Teste de conexão Grok falhou: {e}")
            return False


# Registrar provedor na factory
LLMProviderFactory.register_provider(
    LLMProvider.XAI_GROK, 
    GrokProvider
)