#!/bin/sh

# Fail on any error
set -e

# Variáveis de ambiente (com valores padrão para segurança)
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
TIMEOUT=60

# Função para verificar a disponibilidade do banco de dados
wait_for_db() {
    echo "Aguardando o banco de dados em ${DB_HOST}:${DB_PORT}..."

    # Loop para verificar a conexão TCP com o banco de dados
    for i in $(seq $TIMEOUT); do
        # nc (netcat) verifica se a porta está aberta. O timeout de 1s evita longa espera.
        if nc -z -w 1 "${DB_HOST}" "${DB_PORT}"; then
            echo "Banco de dados está pronto para aceitar conexões."
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo "Erro: Timeout de ${TIMEOUT}s excedido. O banco de dados não ficou disponível."
    return 1
}

# 1. Aguardar o banco de dados estar pronto
wait_for_db

# 2. Executar o script de inicialização do banco de dados
# Este script cria as tabelas e os dados iniciais se necessário.
echo "Aplicando migrações do banco de dados..."
flask db upgrade
echo "Migrações concluídas."

# 3. Iniciar a aplicação Flask com Gunicorn
# 'exec' substitui o processo do shell pelo Gunicorn,
# o que é uma prática recomendada para que os sinais do Docker cheguem corretamente.
echo "Iniciando a aplicação com Gunicorn..."
exec gunicorn src.main:app --bind 0.0.0.0:5000 --workers 4 --log-level info
