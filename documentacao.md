# Documentação do Projeto - Clone do Minhas Economias

## Visão Geral

Este projeto é uma réplica completa do site Minhas Economias (https://wwws.minhaseconomias.com.br/), incluindo todas as funcionalidades principais, interface de usuário e experiência de uso. O sistema foi desenvolvido utilizando Flask (Python) para o backend e HTML/CSS/JavaScript para o frontend, seguindo uma arquitetura MVC (Model-View-Controller).

## Estrutura do Projeto

```
minhas_economias_clone/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── dream.py
│   │   └── budget.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── dreams.py
│   │   ├── budgets.py
│   │   ├── analysis.py
│   │   └── settings.py
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── accounts/
│   │   ├── transactions/
│   │   ├── dreams/
│   │   ├── budgets/
│   │   ├── analysis/
│   │   └── settings/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── main.py
├── venv/
├── requirements.txt
├── checklist_testes.md
└── arquitetura.md
```

## Funcionalidades Implementadas

### 1. Sistema de Autenticação
- Login com email/senha
- Registro de novos usuários
- Recuperação de senha
- Proteção de rotas para usuários autenticados

### 2. Dashboard Principal
- Visão geral financeira
- Listagem de contas e saldos
- Resumo de transações recentes
- Navegação para todas as funcionalidades

### 3. Gerenciamento de Contas
- Criação, edição e exclusão de contas
- Suporte para diferentes tipos de contas:
  - Carteira
  - Conta Corrente
  - Poupança
  - Cartão de Crédito
- Cálculo automático de saldos

### 4. Gerenciamento de Transações
- Registro de entradas e saídas
- Categorização de transações
- Filtros por período e conta
- Edição e exclusão de transações

### 5. Funcionalidades de Sonhos (Metas)
- Criação e gerenciamento de metas financeiras
- Acompanhamento de progresso
- Adição de valores às metas
- Visualização de status e prazos

### 6. Funcionalidades de Orçamentos
- Criação de orçamentos por categoria
- Acompanhamento de gastos vs. orçado
- Filtros por período (mês/ano)
- Visualização de progresso

### 7. Módulos de Análise
- Gráficos de despesas por categoria
- Gráficos de receitas por categoria
- Análise de evolução mensal
- Comparativo receitas x despesas

### 8. Relatórios
- Geração de relatórios mensais
- Geração de relatórios anuais
- Relatórios personalizados por período
- Exportação em diferentes formatos

### 9. Configurações do Usuário
- Gerenciamento de perfil
- Configurações de segurança
- Preferências de moeda e formato de data
- Gerenciamento de categorias
- Exportação de dados
- Exclusão de conta

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Banco de Dados**: SQLite (desenvolvimento), compatível com MySQL/PostgreSQL (produção)
- **Bibliotecas**:
  - Flask-SQLAlchemy (ORM)
  - Chart.js (gráficos)
  - Werkzeug (segurança)

## Instalação e Execução

### Requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Ambiente virtual Python (recomendado)

### Passos para Instalação

1. Clone o repositório:
```
git clone [URL_DO_REPOSITORIO]
cd minhas_economias_clone
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute a aplicação:
```
python src/main.py
```

5. Acesse a aplicação no navegador:
```
http://localhost:5000
```

### Credenciais de Teste
- **Email**: renatolelias@gmail.com
- **Senha**: teste123

## Implantação em Produção

Para implantar em um ambiente de produção, recomenda-se:

1. Configurar um servidor web (Nginx, Apache) com WSGI
2. Utilizar um banco de dados mais robusto (MySQL, PostgreSQL)
3. Implementar HTTPS para segurança
4. Configurar backups regulares do banco de dados
5. Implementar monitoramento e logging

## Considerações de Segurança

- Senhas armazenadas com hash seguro (Werkzeug)
- Proteção contra CSRF em formulários
- Validação de entrada de dados
- Proteção de rotas para usuários autenticados
- Sessões seguras

## Manutenção e Atualizações

O sistema foi projetado com uma arquitetura modular que facilita a manutenção e adição de novas funcionalidades. Para atualizações:

1. Siga o padrão MVC existente
2. Mantenha a consistência visual com o restante da aplicação
3. Execute testes completos antes de implantar atualizações
4. Documente todas as alterações

## Contato e Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato através de [seu_email@exemplo.com].
