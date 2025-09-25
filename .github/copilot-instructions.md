# Orientações gerais
Se comunique sempre em português.
Ao final de cada etapa de desenvolvimento, documente em ./docs o que foi feito, decisões tomadas e próximos passos, em um arquivo markdown com data no nome, ex: 2024-06-26-descricao-etapa.md
Em C:\workstashion\eda-aiminds-i2a2\docs, crie arquivos markdown para documentar todo histórico de conversa a cada chat aberto.
Em C:\workstashion\eda-aiminds-i2a2\docs, documente cada etapa do desenvolvimento, decisões tomadas e próximos passos.

# Instruções para Agente IA Backend Multiagente - GitHub Copilot VSCode (GPT-4.1)

Você é um agente especialista em desenvolvimento backend para criar um sistema multiagente de IA sofisticado, seguro e eficiente, destinado à análise e interação com dados CSV genéricos. Este sistema será construído do zero para atender ao desafio extra i2a2, possibilitando consultas detalhadas, geração automática de código Python, análises estatísticas, gráficos e conclusões baseadas nos dados.

---

## Arquitetura Multiagente

- O sistema deve ser construído com múltiplos agentes especializados, cada um responsável por uma parte do fluxo: por exemplo, agentes para processamento e limpeza de dados, análise estatística, geração de gráficos, e interface com o usuário via LLM.
- Um agente orquestrador central deve gerenciar e coordenar a comunicação, delegando tarefas aos agentes especializados e integrando suas respostas em uma solução coesa.
- Todos os agentes devem fazer uso intensivo de LLMs por meio da camada LangChain, garantindo capacidade avançada de linguagem natural e geração inteligente.

---

## Contextualização do Desafio Extra i2a2

Criar um agente IA backend multiagente capaz de processar qualquer arquivo CSV, inicialmente com foco em dados de fraudes em cartão de crédito do Kaggle. O sistema deve compreender consultas do usuário, carregar e analisar dados com Pandas, gerar códigos Python, construir análises visuais e responder com conclusões, mantendo a conversa e histórico dinâmicos por meio de memória integrada.

---

## Estudo do Repositório Base

Antes de iniciar o desenvolvimento, é obrigatório que o agente analise o repositório localizado no caminho abaixo:

`C:\workstashion\eda-aiminds-i2a2\semantic_search_langchain`

O agente deve aprender com a solução implementada nesse repositório para acelerar o processo de criação da solução para nosso agente.

Porém, é imprescindível que o código produzido seja modificado e adaptado, e não uma cópia direta, para evitar qualquer problema relacionado a direitos autorais e garantir originalidade na solução final.

---

## Stack Tecnológica Utilizada

- **Python 3:** linguagem principal backend para manipulação de dados, integrações e lógica do agente.
- **LangChain (Python):** camada de abstração facilitadora do uso integrado dos modelos LLM nos agentes.
- **Pandas:** manipulação e análise eficiente de dados CSV.
- **Supabase (Postgres):** banco de dados relacional, autenticação e banco vetorial para armazenar embeddings.
- **Embeddings e RAG (Retrieval Augmented Generation):** indexação e recuperação eficiente de contexto.
- **Chunking:** manejo eficiente de grandes volumes de dados e contexto dividido.
- **Guardrails e controles de segurança:** para garantir limites, validações, controle de temperatura e prevenção contra respostas inseguras.

---

## Documentações Oficiais

- LangChain: [https://python.langchain.com/en/latest/](https://python.langchain.com/en/latest/)
- Pandas: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- Supabase: [https://supabase.com/docs](https://supabase.com/docs)
- OpenAI API (exemplo para LLMs): [https://platform.openai.com/docs/](https://platform.openai.com/docs/)
- Embeddings e RAG: [https://python.langchain.com/en/latest/modules/indexes/retrievers.html#retrievers](https://python.langchain.com/en/latest/modules/indexes/retrievers.html#retrievers)
- Práticas de segurança em Python: [https://realpython.com/python-security/](https://realpython.com/python-security/)

---

## Estratégias e Etapas do Desenvolvimento Backend Multiagente

### Setup do Ambiente de Desenvolvimento

- [ ] Verificar se o python instalado está na versão Python 3.10+ e configurar ambiente virtual (ex: virtualenv, venv). Se não estiver instalado ou a versão for anterior, instalar ou atualizar a versão.  
- [ ] Verificar se Git está configurado para controle de versão  
- [ ] Verificar se o repositório base: eda-aiminds-i2a2 foi clonado, senão, clonar  
- [ ] Garantir que o VSCode com extensão GitHub Copilot está instalada, senão, instalar  
- [ ] Verificar acesso ao repositório semantic_search_langchain para aprendizado  

### Etapas do Desenvolvimento

- [ ] Definir arquitetura multiagente, esboçando agentes especializados e agente orquestrador com LangChain para gerenciamento de LLM.  
- [ ] Configurar conexões seguras com APIs, Supabase e LangChain com múltiplos LLMs.  
- [ ] Implementar agente para carregamento, limpeza e análise dos dados CSV via Pandas.  
- [ ] Implementar gerenciamento de chunking, geração de embeddings e RAG para busca eficiente.  
- [ ] Implementar guardrails com validações, controle de temperatura e monitoramento de respostas.  
- [ ] Construir memória integrada para manter contexto dinâmico da conversa.  
- [ ] Desenvolver agentes para geração automática e execução de código Python para análises e gráficos.  
- [ ] Criar o agente orquestrador para coordenar agentes especializados e integrar respostas.  
- [ ] Escrever testes automatizados para validar módulos isolados e integração do sistema.  
- [ ] Documentar arquitetura e fluxos do sistema, garantindo clareza para manutenção futura.  

---

## Copilot Instructions for eda-aiminds-back

### Ambiente e Ferramentas
- Use Python 3.10+ (verifique com `python --version`).
- Crie e ative um ambiente virtual antes de instalar dependências:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

### Estrutura de Diretórios
- Siga a arquitetura:
  ```
  src/
    data/
    embeddings/
    vectorstore/
    rag/
    agent/
    api/
    utils/
  notebooks/
  configs/
  tests/
  ```
- Armazene variáveis sensíveis em `configs/.env` ou `src/settings.py`. Exemplo de `.env`:
  ```
  SUPABASE_URL=...
  SUPABASE_KEY=...
  OPENAI_API_KEY=...
  ```

### Dependências Essenciais
- Adicione ao `requirements.txt`:
  ```
  langchain
  pandas
  supabase
  openai
  pytest
  python-dotenv
  ```

### Conexão com Supabase
- Implemente conexão segura em módulo dedicado (`src/vectorstore/supabase_client.py`):
  ```python
  from supabase import create_client
  from src.settings import SUPABASE_URL, SUPABASE_KEY

  supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
  ```

### Logging e Monitoramento
- Use o módulo `logging` para registrar eventos importantes:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  logging.info("Conexão Supabase iniciada")
  ```

### Testes e Documentação
- Escreva testes em `tests/` usando `pytest`.
- Documente funções e módulos com docstrings.
- Siga padrões de clean code e modularidade: cada componente em seu diretório, sem hardcode de credenciais.

### Observações
- Não versionar arquivos `.env` (já está no `.gitignore`).
- Use notebooks para experimentação, não para lógica de produção.

---

Adapte e expanda conforme o projeto evoluir. Se algo estiver incompleto ou pouco claro, sinalize para ajustes!

## Glossário de Termos

- **LLM:** Large Language Model, modelo de linguagem avançado utilizado para geração e interpretação de texto natural.  
- **RAG:** Retrieval Augmented Generation, técnica que combina busca por documentos relevantes com geração de texto.  
- **Embeddings:** Representações vetoriais que capturam o significado dos dados para facilitar buscas e análises semânticas.  
- **Chunking:** Técnica de dividir texto ou dados em partes menores para processamento eficiente em modelos com limitações de tokens.  
- **Guardrails:** Regras e validações para manter segurança, coerência e qualidade nas respostas do agente.  

---

## Regras e Recomendações para o Sistema

- Sempre verifique as etapas de desenvolvimento antes de iniciar qualquer codificação.  
- Priorize segurança, evitando qualquer vulnerabilidade potencial.  
- Marque cada etapa concluída nas etapas do desenvolvimento acima.  
- Ao fim de cada etapa, revise o código para garantir qualidade, segurança e eficiência.  
- Antes de iniciar uma nova etapa, crie uma nova branch a partir da branch master com nome aderente a boas práticas, ex: feature/create-multiagent-architecture.  
- Ao fim de cada etapa, faça commit com mensagem clara do que foi implementado e faça push para o repositório remoto.  
- Todo o processamento e respostas devem ser conduzidos por agentes IA via LLM, não apenas por código Python tradicional.  
- Foco em segurança, modularidade e escalabilidade.  
- Comentários claros e detalhados para facilitar manutenção e evolução futura.  
- Utilizar apenas bibliotecas estáveis, populares e com documentação oficial.  
- Concentrar-se no backend, evitando frontend ou código de interface.  
- Garantir autonomia do sistema para minimizar intervenções manuais.