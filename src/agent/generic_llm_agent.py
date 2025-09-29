"""Agente LLM genérico com suporte múltiplos provedores (Google, Grok, etc.)
=========================================================================

Este agente utiliza diferentes provedores LLM através de uma interface unificada.
Integra com sistema RAG para cache inteligente e funciona com o sistema multiagente.
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from typing import Dict, Any, Optional, List
import json
from dataclasses import dataclass

from src.agent.base_agent import BaseAgent, AgentError
from src.llm.manager import llm_manager
from src.llm.base import LLMRequest, LLMResponse, LLMProvider, create_system_prompt
from src.utils.logging_config import get_logger

# Import condicional do sistema RAG
try:
    from src.embeddings.vector_store import VectorStore
    from src.embeddings.generator import EmbeddingGenerator, EmbeddingProvider
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    VectorStore = None
    EmbeddingGenerator = None

logger = get_logger(__name__)


class GenericLLMAgent(BaseAgent):
    """Agente LLM genérico com suporte a múltiplos provedores."""
    
    def __init__(self, 
                 name: str = "generic_llm", 
                 provider_type: Optional[str] = None,
                 model: Optional[str] = None):
        """Inicializa agente LLM genérico.
        
        Args:
            name: Nome do agente
            provider_type: Tipo do provedor (google_gemini, xai_grok, etc.)
            model: Modelo específico a usar
        """
        super().__init__(name, "Agente LLM genérico com suporte a múltiplos provedores")
        
        self.logger = logger
        
        # Configurar provedor LLM
        try:
            if provider_type:
                self.llm_provider = llm_manager.create_provider(
                    provider_type=provider_type,
                    model=model
                )
            else:
                self.llm_provider = llm_manager.get_default_provider()
                
            self.provider_name = self.llm_provider.name
            self.logger.info(f"LLM Provider configurado: {self.provider_name}")
            
        except Exception as e:
            raise AgentError(self.name, f"Erro ao configurar provedor LLM: {e}")
        
        # Configurar sistema RAG se disponível
        self.rag_enabled = False
        if RAG_AVAILABLE:
            try:
                self.vector_store = VectorStore()
                self.embedding_generator = EmbeddingGenerator(provider=EmbeddingProvider.SENTENCE_TRANSFORMER)
                self.rag_enabled = True
                self.logger.info("RAG integrado ao LLM Agent")
            except Exception as e:
                self.logger.warning(f"RAG não disponível: {e}")
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa consulta usando sistema híbrido RAG + LLM.
        
        Fluxo:
        1. Se RAG disponível, busca consultas similares no cache vetorial
        2. Se encontrar resposta relevante, usa ela (cache inteligente)  
        3. Se não encontrar, chama LLM do provedor configurado
        4. Salva consulta + resposta LLM no banco vetorial
        
        Args:
            query: Consulta/prompt para o LLM
            context: Contexto adicional (dados, configurações, etc.)
            
        Returns:
            Resposta estruturada do LLM ou cache
        """
        try:
            # 1. BUSCAR NO CACHE VETORIAL (se disponível)
            if self.rag_enabled:
                cached_response = self._search_cached_response(query)
                if cached_response:
                    self.logger.info("💾 Usando resposta em cache (RAG)")
                    return self._build_response(
                        cached_response["content"],
                        metadata={
                            "provider": "cache_rag", 
                            "model": "vector_cache",
                            "llm_used": False,
                            "cache_used": True,
                            "similarity_score": cached_response.get("similarity", 0.0),
                            "success": True
                        }
                    )
            
            # 2. GERAR NOVA RESPOSTA COM LLM
            self.logger.info(f"🤖 Gerando nova resposta com {self.provider_name}")
            
            # Preparar request
            llm_request = self._prepare_llm_request(query, context)
            
            # Chamar provedor LLM
            llm_response = self.llm_provider.generate(llm_request)
            
            if not llm_response.success:
                raise AgentError(
                    self.name, 
                    f"Erro no LLM: {llm_response.error_message}"
                )
            
            # 3. SALVAR NO CACHE VETORIAL
            if self.rag_enabled:
                cache_saved = self._save_to_vector_store(query, llm_response.content, context)
                if cache_saved:
                    self.logger.info("💾 Consulta salva no cache vetorial")
                else:
                    self.logger.warning("Falha ao salvar no cache vetorial")
            
            # 4. RETORNAR RESPOSTA ESTRUTURADA
            return self._build_response(
                llm_response.content,
                metadata={
                    "provider": llm_response.provider.value,
                    "model": llm_response.model,
                    "llm_used": True,
                    "cache_used": False,
                    "processing_time": llm_response.processing_time,
                    "usage": llm_response.usage,
                    "success": True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro no processamento LLM: {e}")
            return self._build_error_response(str(e))
    
    def _prepare_llm_request(self, query: str, context: Optional[Dict[str, Any]] = None) -> LLMRequest:
        """Prepara request para o LLM."""
        
        # Determinar tipo de análise para system prompt
        analysis_type = "general"
        if context:
            if "fraud_data" in context or "fraude" in query.lower():
                analysis_type = "fraud_detection"
            elif "correlacao" in query.lower() or "correlation" in query.lower():
                analysis_type = "correlation_analysis"
        
        # Criar system prompt
        system_prompt = create_system_prompt(analysis_type)
        
        return LLMRequest(
            prompt=query,
            context=context,
            system_prompt=system_prompt,
            temperature=self.llm_provider.config.default_temperature,
            max_tokens=self.llm_provider.config.default_max_tokens
        )
    
    def _search_cached_response(self, query: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Busca respostas similares no cache vetorial."""
        if not self.rag_enabled:
            return None
            
        try:
            # Gerar embedding da consulta
            query_result = self.embedding_generator.generate_embedding(query)
            query_embedding = query_result.embedding  # Extrair lista de floats
            
            # Buscar consultas similares
            results = self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=1,
                similarity_threshold=similarity_threshold
            )
            
            if results and len(results) > 0:
                best_match = results[0]
                self.logger.info(f"🎯 Cache hit! Similaridade: {best_match.similarity_score:.3f}")
                
                return {
                    "content": best_match.metadata.get("response", ""),
                    "similarity": best_match.similarity_score,
                    "original_query": best_match.chunk_text
                }
                
        except Exception as e:
            self.logger.warning(f"Erro na busca de cache: {e}")
            
        return None
    
    def _save_to_vector_store(self, query: str, response: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Salva consulta e resposta no banco vetorial para cache futuro."""
        if not self.rag_enabled:
            return False
            
        try:
            # Gerar e salvar embedding
            query_result = self.embedding_generator.generate_embedding(query)
            query_embedding = query_result.embedding  # Extrair lista de floats
            
            result = self.vector_store.store_embedding(
                query=query,
                response=response,
                embedding=query_embedding
            )
            
            return bool(result)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar no cache: {e}")
            return False
    
    def switch_provider(self, provider_type: str, model: Optional[str] = None) -> bool:
        """Troca provedor LLM dinamicamente."""
        try:
            new_provider = llm_manager.create_provider(
                provider_type=provider_type,
                model=model
            )
            
            # Testar novo provedor
            if llm_manager.test_provider(new_provider):
                self.llm_provider = new_provider
                self.provider_name = new_provider.name
                self.logger.info(f"Provedor alterado para: {self.provider_name}")
                return True
            else:
                self.logger.error(f"Teste do novo provedor falhou: {provider_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao trocar provedor: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provedor atual."""
        return {
            "name": self.provider_name,
            "provider": self.llm_provider.provider.value,
            "model": self.llm_provider.model,
            "rag_enabled": self.rag_enabled,
            "config": {
                "temperature": self.llm_provider.config.default_temperature,
                "max_tokens": self.llm_provider.config.default_max_tokens
            }
        }
    
    def list_available_providers(self) -> Dict[str, Any]:
        """Lista provedores disponíveis."""
        return llm_manager.get_available_providers()
    
    def _build_response(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói resposta padronizada."""
        return {
            "content": content,
            "agent": self.name,
            "success": True,
            "metadata": metadata
        }
    
    def _build_error_response(self, error_message: str) -> Dict[str, Any]:
        """Constrói resposta de erro."""
        return {
            "content": f"Erro no agente LLM: {error_message}",
            "agent": self.name,
            "success": False,
            "metadata": {
                "error": error_message,
                "provider": getattr(self, 'provider_name', 'unknown')
            }
        }
    
    def analyze_fraud_data(self, fraud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise especializada de dados de fraude.""" 
        prompt = f"""Analise os dados de fraude fornecidos e forneça insights detalhados:

DADOS DE FRAUDE:
{json.dumps(fraud_data, indent=2, ensure_ascii=False)}

Forneça uma análise especializada incluindo:

1. **Análise de Risco**: Avalie o nível de risco atual
2. **Padrões de Fraude**: Identifique características comuns das fraudes
3. **Fatores de Risco**: Quais variáveis mais indicam fraude?
4. **Estratégias de Prevenção**: Como reduzir fraudes futuras?
5. **Alertas Críticos**: Situações que requerem atenção imediata

Use dados concretos e seja específico nas recomendações."""
        
        context = {"analysis_type": "fraud_detection", "fraud_data": fraud_data}
        
        return self.process(prompt, context)
    
    def explain_correlations(self, correlation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explica correlações de forma acessível para negócios."""
        
        prompt = f"""Explique as correlações nos dados de forma acessível para stakeholders de negócio:

CORRELAÇÕES ENCONTRADAS:
{json.dumps(correlation_data, indent=2, ensure_ascii=False)}

Explique:
1. **O que significam** essas correlações em termos práticos
2. **Implicações de negócio** de cada correlação importante
3. **Oportunidades** identificadas através das correlações
4. **Riscos** potenciais revelados pelos dados
5. **Ações recomendadas** baseadas nessas descobertas

Use linguagem acessível e evite jargão estatístico excessivo."""
        
        context = {"analysis_type": "correlation_analysis", "correlation_data": correlation_data}
        
        return self.process(prompt, context)


# Alias para compatibilidade com código existente
GoogleLLMAgent = GenericLLMAgent