# Arquitetura do Projeto - Clone do Minhas Economias

## Visão Geral

Este documento descreve a arquitetura planejada para a replicação do site Minhas Economias, incluindo todas as funcionalidades, UI e UX observadas durante a análise do sistema original.

## Tecnologias Escolhidas

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (com possível uso de bibliotecas como jQuery)
- **Banco de Dados**: MySQL
- **Autenticação**: Sistema próprio + integração com Google e Facebook OAuth

## Estrutura do Projeto

```
minhas_economias_clone/
├── venv/                      # Ambiente virtual Python
├── src/                       # Código-fonte principal
│   ├── main.py                # Ponto de entrada da aplicação
│   ├── models/                # Modelos de dados
│   │   ├── __init__.py
│   │   ├── user.py            # Modelo de usuário
│   │   ├── account.py         # Modelo de contas (carteira, cartão, etc)
│   │   ├── transaction.py     # Modelo de transações
│   │   ├── category.py        # Modelo de categorias
│   │   ├── dream.py           # Modelo de sonhos/metas
│   │   └── budget.py          # Modelo de orçamentos
│   ├── routes/                # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py            # Rotas de autenticação
│   │   ├── dashboard.py       # Rotas da página inicial/dashboard
│   │   ├── accounts.py        # Rotas para gerenciamento de contas
│   │   ├── transactions.py    # Rotas para transações
│   │   ├── dreams.py          # Rotas para sonhos/metas
│   │   ├── budget.py          # Rotas para orçamentos
│   │   └── analysis.py        # Rotas para análises e relatórios
│   ├── static/                # Arquivos estáticos
│   │   ├── css/               # Estilos CSS
│   │   ├── js/                # Scripts JavaScript
│   │   └── img/               # Imagens e ícones
│   └── templates/             # Templates HTML
│       ├── base.html          # Template base
│       ├── auth/              # Templates de autenticação
│       ├── dashboard/         # Templates do dashboard
│       ├── accounts/          # Templates de contas
│       ├── transactions/      # Templates de transações
│       ├── dreams/            # Templates de sonhos/metas
│       ├── budget/            # Templates de orçamentos
│       └── analysis/          # Templates de análises
└── requirements.txt           # Dependências do projeto
```

## Modelo de Dados

### Usuário (User)
- id (PK)
- email
- senha_hash
- nome
- data_cadastro
- ultimo_acesso
- configuracoes (JSON)

### Conta (Account)
- id (PK)
- usuario_id (FK)
- tipo (carteira, cartão de crédito, conta corrente, poupança)
- nome
- saldo_atual
- data_criacao
- ativo (boolean)

### Categoria (Category)
- id (PK)
- usuario_id (FK)
- nome
- tipo (receita, despesa)
- cor
- icone
- ordem

### Transação (Transaction)
- id (PK)
- usuario_id (FK)
- conta_id (FK)
- categoria_id (FK)
- descricao
- valor
- data
- tipo (entrada, saída)
- consolidada (boolean)
- recorrente (boolean)
- frequencia_recorrencia (se aplicável)

### Sonho/Meta (Dream)
- id (PK)
- usuario_id (FK)
- tipo (viagem, carro, eletrônico, casa, etc)
- nome
- valor_total
- valor_atual
- data_criacao
- data_alvo
- status (ativo, concluído, cancelado)

### Orçamento (Budget)
- id (PK)
- usuario_id (FK)
- nome
- periodo (mensal, anual)
- data_inicio
- data_fim
- ativo (boolean)

### Item de Orçamento (BudgetItem)
- id (PK)
- orcamento_id (FK)
- categoria_id (FK)
- valor_planejado
- valor_realizado

## Funcionalidades Principais

### 1. Autenticação
- Login com email/senha
- Login com Google
- Login com Facebook
- Recuperação de senha
- Lembrar usuário

### 2. Dashboard
- Visão geral de contas e saldos
- Entradas e saídas do período
- Transações recentes
- Alertas de orçamento

### 3. Gerenciamento de Contas
- Adicionar/editar/remover contas
- Visualizar saldo por conta
- Transferências entre contas

### 4. Transações
- Adicionar/editar/remover transações
- Filtrar por período, categoria, conta
- Busca rápida
- Exportação de dados

### 5. Sonhos/Metas
- Criar metas financeiras
- Acompanhar progresso
- Categorizar por tipo (viagem, carro, etc)

### 6. Orçamento
- Criar orçamentos mensais/anuais
- Definir limites por categoria
- Acompanhar gastos vs. orçamento

### 7. Análise
- Gráficos de gastos por categoria
- Relatórios personalizados
- Evolução patrimonial

### 8. Configurações
- Informações pessoais
- Categorização automática
- Preferências de notificação

## Fluxos de Usuário

### Fluxo de Login
1. Usuário acessa a página inicial
2. Insere email e senha ou escolhe login social
3. Sistema valida credenciais
4. Redireciona para dashboard

### Fluxo de Registro de Transação
1. Usuário acessa a aba "Transações"
2. Clica em "Adicionar transação"
3. Preenche dados (valor, data, categoria, conta)
4. Confirma a transação
5. Sistema atualiza saldo e exibe confirmação

### Fluxo de Criação de Meta
1. Usuário acessa a aba "Sonhos"
2. Escolhe tipo de sonho/meta
3. Preenche detalhes (nome, valor, data alvo)
4. Confirma a criação
5. Sistema exibe a meta na lista de sonhos

## Considerações de UI/UX

- Manter a mesma paleta de cores do site original (verde, azul, branco)
- Preservar a navegação por abas no topo
- Manter a mesma estrutura de menus e submenus
- Replicar os ícones e elementos visuais
- Garantir responsividade para diferentes dispositivos
- Manter os mesmos fluxos de interação

## Requisitos Técnicos

- Sistema de autenticação seguro com hash de senhas
- Validação de formulários no cliente e servidor
- Proteção contra CSRF e XSS
- Backup automático de dados
- Logs de atividades importantes
- Tratamento de erros e exceções
- Testes unitários e de integração
