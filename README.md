# EDA AI Minds Backend

Sistema multiagente para análise inteligente de dados CSV com LangChain, Supabase e vetorização.

## 🚀 Características

- **Sistema Multiagente**: Arquitetura com agentes especializados (CSV, RAG, Base)
- **Análise CSV Inteligente**: Processamento automatizado com detecção de fraudes
- **Sistema RAG Completo**: Chunking, embeddings e busca vetorial
- **Banco Vetorial**: PostgreSQL + pgvector para similaridade semântica
- **LLM Integration**: Suporte a OpenAI, Google GenAI, Perplexity Sonar
- **Fallbacks Robustos**: Funciona mesmo sem credenciais ou conexão

## 🛠️ Instalação

### Pré-requisitos

- Python 3.10+ 
- PostgreSQL com extensão pgvector
- Supabase account (opcional)

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/ai-mindsgroup/eda-aiminds-back.git
cd eda-aiminds-back

# Crie ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### Opções de Instalação

```bash
# Instalação completa (recomendado)
pip install -r requirements.txt

# Instalação mínima (só CSV + PostgreSQL)
pip install -r requirements-minimal.txt

# Instalação para desenvolvimento
pip install -r requirements-dev.txt
```

## ⚙️ Configuração

1. **Copie o arquivo de configuração**:
```bash
cp configs/.env.example configs/.env
```

2. **Configure suas credenciais**:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# APIs LLM (opcional)
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
SONAR_API_KEY=your-perplexity-key

# PostgreSQL
DB_HOST=db.your-project.supabase.co
DB_PASSWORD=your-password
```

3. **Execute as migrations**:
```bash
python scripts/run_migrations.py
```

4. **Teste a instalação**:
```bash
python test_simple.py
```

## 🧪 Testes

### Teste Rápido
```bash
# Teste componentes básicos
python test_simple.py

# Teste agente CSV
python demo_csv_agent.py

# Teste sistema RAG (requer credenciais)
python test_rag_system.py
```

### Testes com Pytest
```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Executar testes
pytest tests/ -v
```

## 📊 Funcionalidades

### 1. Análise CSV
- Carregamento automático com detecção de encoding
- Estatísticas descritivas e correlações
- Detecção especializada de fraudes
- Sugestões de visualizações
- Interface em português

### 2. Sistema RAG
- **Chunking**: 5 estratégias (sentence, paragraph, fixed_size, etc.)
- **Embeddings**: Sentence Transformers + OpenAI API  
- **Vector Store**: Busca por similaridade no Supabase
- **Generation**: Respostas contextualizadas via LLM

### 3. Agentes Multiagente
- **BaseAgent**: Classe abstrata padronizada
- **CSVAnalysisAgent**: Especialista em dados tabulares
- **RAGAgent**: Recuperação e geração aumentada
- **Orquestrador**: Coordenação entre agentes (planejado)

## 🏗️ Arquitetura

```
src/
├── agent/           # Agentes especializados
├── embeddings/      # Sistema de embeddings e RAG
├── vectorstore/     # Cliente Supabase
├── api/            # Integrações externas  
├── utils/          # Utilitários (logging, etc.)
└── settings.py     # Configurações centralizadas

migrations/         # Scripts SQL do banco
scripts/           # Utilitários de setup
docs/             # Documentação e relatórios
configs/          # Arquivos de configuração
```

## 📚 Uso Básico

### Análise CSV
```python
from src.agent.csv_analysis_agent import CSVAnalysisAgent

# Criar agente
agent = CSVAnalysisAgent()

# Carregar dados
result = agent.load_csv("dados.csv")

# Analisar
analysis = agent.process("Quantas fraudes foram detectadas?")
print(analysis['content'])
```

### Sistema RAG
```python
from src.agent.rag_agent import RAGAgent
from src.embeddings.generator import EmbeddingProvider

# Criar agente RAG  
rag = RAGAgent(embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMER)

# Ingerir documentos
rag.ingest_text("Conteúdo do documento...", source_id="doc1")

# Consultar
response = rag.process("Como detectar fraudes?")
print(response['content'])
```

## 🔧 Stack Tecnológico

- **Python 3.10+** com type annotations
- **LangChain 0.3+** para orquestração de LLMs
- **Pandas 2.2+** para manipulação de dados
- **PostgreSQL + pgvector** para busca vetorial
- **Sentence Transformers** para embeddings (384D)
- **Supabase** como backend-as-a-service
- **PyTorch 2.8** para deep learning
- **Matplotlib/Seaborn** para visualizações

## 📈 Status do Projeto

- ✅ **Sistema de Embeddings RAG** (100%)
- ✅ **Análise CSV Inteligente** (100%) 
- ✅ **Banco Vetorial** (100%)
- ✅ **Integração LLM** (100%)
- ✅ **Sistema de Logging** (100%)
- ❌ **Agente Orquestrador** (planejado)

**Progresso geral: 75% concluído**

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

- **Documentação**: Veja `docs/` para documentação detalhada
- **Issues**: Reporte bugs no GitHub Issues  
- **Discussões**: Use GitHub Discussions para dúvidas

---

Desenvolvido com ❤️ para o desafio i2a2 - AI Minds Group
