"""Provedor Google Gemini para o sistema LLM genérico."""
import google.generativeai as genai
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


class GoogleGeminiProvider(BaseLLMProvider):
    """Provedor para Google Gemini API."""
    
    def __init__(self, config: LLMConfig):
        """Inicializa provedor Google Gemini."""
        super().__init__(config)
        self.logger = logger
        
    def _initialize_client(self) -> None:
        """Inicializa cliente Google Gemini."""
        try:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
            self.logger.info(f"Google Gemini inicializado: {self.model}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Google Gemini: {e}")
            raise
    
    def _call_api(self, request: LLMRequest) -> LLMResponse:
        """Chama Google Gemini API."""
        try:
            # Preparar prompt final
            if request.system_prompt and request.context:
                full_prompt = f"{request.system_prompt}\n\nContexto:\n{request.context}\n\nConsulta: {request.prompt}"
            elif request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\nConsulta: {request.prompt}"
            else:
                full_prompt = request.prompt
            
            # Configurar parâmetros de geração
            generation_config = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "candidate_count": 1,
            }
            
            # Gerar resposta
            response = self._client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extrair conteúdo
            content = response.text if response.text else "Sem resposta gerada"
            
            # Metadados de uso (Gemini não fornece detalhes via API gratuita)
            usage = {
                "prompt_tokens": "n/a",
                "completion_tokens": "n/a", 
                "total_tokens": "n/a",
                "estimated_prompt_chars": len(full_prompt),
                "response_chars": len(content)
            }
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.GOOGLE_GEMINI,
                model=self.model,
                success=True,
                usage=usage
            )
            
        except Exception as e:
            self.logger.error(f"Erro na API Google Gemini: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.GOOGLE_GEMINI,
                model=self.model,
                success=False,
                error_message=str(e)
            )
    
    def validate_config(self) -> bool:
        """Valida configuração específica do Google Gemini."""
        if not super().validate_config():
            return False
            
        # Verificar se modelo é suportado
        supported_models = [
            "gemini-pro", "gemini-1.5-pro", "gemini-2.0-flash-exp",
            "gemini-1.5-flash", "gemini-2.0-flash"
        ]
        
        return self.model in supported_models


# Registrar provedor na factory
LLMProviderFactory.register_provider(
    LLMProvider.GOOGLE_GEMINI, 
    GoogleGeminiProvider
)