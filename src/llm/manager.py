"""Gerenciador de configuração e criação de provedores LLM."""
from typing import Dict, Any, Optional
from src.llm.base import (
    LLMProvider, 
    LLMConfig, 
    BaseLLMProvider,
    LLMProviderFactory
)
from src.settings import (
    GOOGLE_API_KEY, 
    XAI_API_KEY,
    GROQ_API_KEY,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_GOOGLE_MODEL, 
    DEFAULT_GROK_MODEL,
    DEFAULT_GROQ_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Importar provedores para registrá-los na factory
from src.llm.google_provider import GoogleGeminiProvider
from src.llm.grok_provider import GrokProvider
from src.llm.groq_provider import GroqProvider


class LLMManager:
    """Gerenciador central para provedores LLM."""
    
    def __init__(self):
        self.logger = logger
        self._active_provider: Optional[BaseLLMProvider] = None
        
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Retorna provedores disponíveis com suas configurações."""
        providers = {
            "google_gemini": {
                "name": "Google Gemini",
                "models": ["gemini-pro", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"],
                "api_key_available": bool(GOOGLE_API_KEY),
                "default_model": DEFAULT_GOOGLE_MODEL
            },
            "xai_grok": {
                "name": "xAI Grok", 
                "models": ["grok-beta", "grok-2-1212", "grok-2-vision-1212", "grok-2-public-beta"],
                "api_key_available": bool(XAI_API_KEY),
                "default_model": DEFAULT_GROK_MODEL
            },
            "groq": {
                "name": "Groq",
                "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "llama-3.1-70b-versatile"],
                "api_key_available": bool(GROQ_API_KEY),
                "default_model": DEFAULT_GROQ_MODEL
            }
        }
        return providers
    
    def create_provider(self, 
                       provider_type: str, 
                       model: Optional[str] = None,
                       api_key: Optional[str] = None,
                       **kwargs) -> BaseLLMProvider:
        """Cria provedor LLM baseado no tipo."""
        
        # Mapear string para enum
        provider_mapping = {
            "google_gemini": LLMProvider.GOOGLE_GEMINI,
            "xai_grok": LLMProvider.XAI_GROK,
            "groq": LLMProvider.GROQ,
            "openai_gpt": LLMProvider.OPENAI_GPT,
            "anthropic_claude": LLMProvider.ANTHROPIC_CLAUDE
        }
        
        provider_enum = provider_mapping.get(provider_type)
        if not provider_enum:
            raise ValueError(f"Provedor não suportado: {provider_type}")
        
        # Configurar API key e modelo padrão
        if provider_enum == LLMProvider.GOOGLE_GEMINI:
            api_key = api_key or GOOGLE_API_KEY
            model = model or DEFAULT_GOOGLE_MODEL
            
        elif provider_enum == LLMProvider.XAI_GROK:
            api_key = api_key or XAI_API_KEY
            model = model or DEFAULT_GROK_MODEL
            
        elif provider_enum == LLMProvider.GROQ:
            api_key = api_key or GROQ_API_KEY
            model = model or DEFAULT_GROQ_MODEL
            
        if not api_key:
            raise ValueError(f"API key não encontrada para {provider_type}")
        
        # Criar configuração
        config = LLMConfig(
            provider=provider_enum,
            model=model,
            api_key=api_key,
            default_temperature=kwargs.get('temperature', LLM_TEMPERATURE),
            default_max_tokens=kwargs.get('max_tokens', LLM_MAX_TOKENS),
            base_url=kwargs.get('base_url')
        )
        
        # Validar configuração
        if not self._validate_provider_config(config):
            raise ValueError(f"Configuração inválida para {provider_type}")
        
        # Criar provedor
        provider = LLMProviderFactory.create_provider(config)
        
        self.logger.info(f"Provedor LLM criado: {provider.name}")
        return provider
    
    def get_default_provider(self) -> BaseLLMProvider:
        """Retorna provedor padrão baseado nas configurações."""
        if self._active_provider:
            return self._active_provider
            
        try:
            self._active_provider = self.create_provider(DEFAULT_LLM_PROVIDER)
            return self._active_provider
            
        except Exception as e:
            self.logger.error(f"Erro ao criar provedor padrão {DEFAULT_LLM_PROVIDER}: {e}")
            
            # Fallback: tentar outros provedores disponíveis
            available = self.get_available_providers()
            for provider_type, info in available.items():
                if info["api_key_available"] and provider_type != DEFAULT_LLM_PROVIDER:
                    try:
                        self.logger.info(f"Tentando fallback para {provider_type}")
                        self._active_provider = self.create_provider(provider_type)
                        return self._active_provider
                    except Exception as fallback_error:
                        self.logger.warning(f"Fallback para {provider_type} falhou: {fallback_error}")
                        continue
            
            raise Exception("Nenhum provedor LLM disponível")
    
    def set_active_provider(self, provider: BaseLLMProvider) -> None:
        """Define provedor ativo."""
        self._active_provider = provider
        self.logger.info(f"Provedor ativo alterado para: {provider.name}")
    
    def _validate_provider_config(self, config: LLMConfig) -> bool:
        """Valida configuração do provedor."""
        try:
            # Criar instância temporária para validação
            temp_provider = LLMProviderFactory.create_provider(config)
            return temp_provider.validate_config()
        except Exception as e:
            self.logger.error(f"Erro na validação de configuração: {e}")
            return False
    
    def test_provider(self, provider: BaseLLMProvider) -> bool:
        """Testa se provedor está funcionando."""
        try:
            from src.llm.base import LLMRequest
            
            test_request = LLMRequest(
                prompt="Teste de funcionamento. Responda apenas 'OK'.",
                temperature=0.1,
                max_tokens=10
            )
            
            response = provider.generate(test_request)
            success = response.success and "ok" in response.content.lower()
            
            if success:
                self.logger.info(f"Teste do provedor {provider.name} passou")
            else:
                self.logger.warning(f"Teste do provedor {provider.name} falhou: {response.error_message}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Erro no teste do provedor {provider.name}: {e}")
            return False


# Instância global do gerenciador
llm_manager = LLMManager()