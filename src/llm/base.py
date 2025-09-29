"""Sistema base para provedores LLM genéricos.

Este módulo define a interface comum para diferentes provedores de LLM
(Google Gemini, xAI Grok, OpenAI GPT, etc.), permitindo troca fácil entre eles.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time


class LLMProvider(Enum):
    """Tipos de provedores LLM suportados."""
    GOOGLE_GEMINI = "google_gemini"
    XAI_GROK = "xai_grok"
    GROQ = "groq"
    OPENAI_GPT = "openai_gpt"
    ANTHROPIC_CLAUDE = "anthropic_claude"


@dataclass
class LLMRequest:
    """Estrutura padronizada para requests LLM."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = 0.3
    max_tokens: int = 1000
    system_prompt: Optional[str] = None


@dataclass  
class LLMResponse:
    """Estrutura padronizada para respostas LLM."""
    content: str
    provider: LLMProvider
    model: str
    success: bool
    error_message: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    
    
@dataclass
class LLMConfig:
    """Configuração de um provedor LLM."""
    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    default_temperature: float = 0.3
    default_max_tokens: int = 1000


class BaseLLMProvider(ABC):
    """Classe base abstrata para provedores LLM."""
    
    def __init__(self, config: LLMConfig):
        """Inicializa o provedor com configuração."""
        self.config = config
        self.provider = config.provider
        self.model = config.model
        self.api_key = config.api_key
        self._client = None
        
    @abstractmethod
    def _initialize_client(self) -> None:
        """Inicializa cliente específico do provedor."""
        pass
    
    @abstractmethod
    def _call_api(self, request: LLMRequest) -> LLMResponse:
        """Chama API específica do provedor."""
        pass
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Interface pública para gerar resposta."""
        start_time = time.time()
        
        try:
            # Inicializar cliente se necessário
            if self._client is None:
                self._initialize_client()
                
            # Chamar API específica
            response = self._call_api(request)
            response.processing_time = time.time() - start_time
            
            return response
            
        except Exception as e:
            return LLMResponse(
                content="",
                provider=self.provider,
                model=self.model,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def validate_config(self) -> bool:
        """Valida configuração do provedor."""
        return bool(self.api_key and self.model)
    
    @property
    def name(self) -> str:
        """Nome do provedor."""
        return f"{self.provider.value}:{self.model}"


class LLMProviderFactory:
    """Factory para criar provedores LLM."""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, provider_type: LLMProvider, provider_class):
        """Registra um novo tipo de provedor."""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_provider(cls, config: LLMConfig) -> BaseLLMProvider:
        """Cria instância do provedor baseado na configuração."""
        provider_class = cls._providers.get(config.provider)
        
        if not provider_class:
            raise ValueError(f"Provedor não suportado: {config.provider}")
        
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[LLMProvider]:
        """Retorna lista de provedores disponíveis."""
        return list(cls._providers.keys())


def create_system_prompt(analysis_type: str = "general") -> str:
    """Cria prompt de sistema baseado no tipo de análise."""
    
    base_prompt = """Você é um especialista em análise de dados e ciência de dados com PhD em Estatística.
Você foca em fornecer insights práticos e acionáveis para negócios."""
    
    prompts = {
        "fraud_detection": f"""{base_prompt}
        
Especialização: Detecção de fraudes em transações financeiras.
- Identifique padrões suspeitos e anomalias
- Forneça recomendações específicas de prevenção
- Use dados estatísticos para sustentar conclusões""",
        
        "correlation_analysis": f"""{base_prompt}
        
Especialização: Análise de correlações e relações entre variáveis.
- Explique significado prático das correlações
- Identifique oportunidades e riscos de negócio
- Use linguagem acessível para stakeholders""",
        
        "general": base_prompt
    }
    
    return prompts.get(analysis_type, prompts["general"])