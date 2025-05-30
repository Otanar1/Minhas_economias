# Plano de Migração para MySQL - Minhas Economias Clone

## 1. Visão Geral
Este documento descreve o plano de migração do banco de dados SQLite para MySQL para o clone do site Minhas Economias. A migração é necessária para resolver problemas de performance e concorrência em ambiente de produção.

## 2. Configuração do Ambiente MySQL

### 2.1 Instalação do MySQL
```bash
# Instalação do MySQL Server
sudo apt-get update
sudo apt-get install -y mysql-server

# Iniciar o serviço MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2.2 Criação do Banco de Dados e Usuário
```sql
CREATE DATABASE minhas_economias;
CREATE USER 'minhas_economias_user'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON minhas_economias.* TO 'minhas_economias_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2.3 Configuração das Variáveis de Ambiente
```bash
# Adicionar ao arquivo .env na raiz do projeto
MYSQL_USER=minhas_economias_user
MYSQL_PASSWORD=senha_segura
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=minhas_economias
```

## 3. Adaptação do Código

### 3.1 Configuração do SQLAlchemy para MySQL
```python
# Configuração para MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

# Otimizações para MySQL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 60,
    'pool_size': 10,
    'max_overflow': 20
}
```

### 3.2 Dependências Adicionais
```
pymysql==1.1.0
cryptography==41.0.4
```

## 4. Migração de Dados

### 4.1 Exportação dos Dados do SQLite
```python
# Script para exportar dados do SQLite para JSON
import sqlite3
import json

conn = sqlite3.connect('minhas_economias.db')
conn.row_factory = sqlite3.Row

# Função para converter uma tabela para JSON
def table_to_json(table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

# Exportar todas as tabelas
tables = ['users', 'accounts', 'categories', 'transactions', 'dreams', 'budgets']
data = {table: table_to_json(table) for table in tables}

# Salvar em arquivo JSON
with open('data_export.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### 4.2 Importação dos Dados para MySQL
```python
# Script para importar dados do JSON para MySQL
import json
import pymysql
from werkzeug.security import generate_password_hash

# Carregar dados do JSON
with open('data_export.json', 'r') as f:
    data = json.load(f)

# Conectar ao MySQL
conn = pymysql.connect(
    host='localhost',
    user='minhas_economias_user',
    password='senha_segura',
    database='minhas_economias'
)
cursor = conn.cursor()

# Importar usuários
for user in data['users']:
    cursor.execute(
        "INSERT INTO users (id, name, email, password, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (user['id'], user['name'], user['email'], user['password'], user['created_at'], user['updated_at'])
    )

# Importar outras tabelas...

conn.commit()
conn.close()
```

## 5. Testes e Validação

### 5.1 Testes de Conexão
```python
# Teste de conexão com MySQL
import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='minhas_economias_user',
        password='senha_segura',
        database='minhas_economias'
    )
    print("Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro de conexão: {str(e)}")
```

### 5.2 Testes Funcionais
- Login e autenticação
- Dashboard e carregamento de dados
- Operações CRUD em todas as entidades
- Performance com múltiplas conexões simultâneas

## 6. Implantação em Produção

### 6.1 Configuração do Ambiente de Produção
```bash
# Variáveis de ambiente para produção
DATABASE_URL=mysql+pymysql://usuario:senha@host:porta/banco
SECRET_KEY=chave_secreta_producao
```

### 6.2 Implantação da Aplicação
```bash
# Atualizar requirements.txt
pip freeze > requirements.txt

# Reimplantar a aplicação
deploy_apply_deployment --type flask --local_dir /home/ubuntu/minhas_economias_clone
```

## 7. Monitoramento e Manutenção

### 7.1 Monitoramento de Performance
- Tempo de resposta das consultas
- Uso de memória e CPU
- Número de conexões simultâneas

### 7.2 Backup Regular
```bash
# Script de backup diário
mysqldump -u minhas_economias_user -p minhas_economias > backup_$(date +%Y%m%d).sql
```

## 8. Rollback (Em Caso de Falha)
- Manter o banco SQLite como backup
- Procedimento para reverter para SQLite em caso de problemas críticos
