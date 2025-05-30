# Checklist de Testes - Clone Minhas Economias

## 1. Sistema de Autenticação
- [ ] Login com credenciais válidas
- [ ] Tentativa de login com credenciais inválidas
- [ ] Recuperação de senha
- [ ] Registro de novo usuário
- [ ] Validação de campos obrigatórios no registro
- [ ] Redirecionamento após login bem-sucedido
- [ ] Logout

## 2. Dashboard Principal
- [ ] Carregamento correto do dashboard após login
- [ ] Exibição do resumo financeiro
- [ ] Exibição da lista de contas
- [ ] Cálculo correto de saldos totais
- [ ] Navegação entre as diferentes abas
- [ ] Responsividade em diferentes tamanhos de tela

## 3. Gerenciamento de Contas
- [ ] Criação de nova conta (todos os tipos)
- [ ] Edição de conta existente
- [ ] Exclusão de conta
- [ ] Validação de campos obrigatórios
- [ ] Atualização automática de saldos no dashboard

## 4. Gerenciamento de Transações
- [ ] Registro de nova transação (entrada)
- [ ] Registro de nova transação (saída)
- [ ] Edição de transação existente
- [ ] Exclusão de transação
- [ ] Categorização de transações
- [ ] Filtros por período
- [ ] Filtros por conta
- [ ] Atualização automática de saldos após transações

## 5. Funcionalidades de Sonhos (Metas)
- [ ] Criação de novo sonho
- [ ] Edição de sonho existente
- [ ] Exclusão de sonho
- [ ] Adição de valores ao sonho
- [ ] Cálculo correto de progresso
- [ ] Atualização de status (ativo, concluído, cancelado)

## 6. Funcionalidades de Orçamentos
- [ ] Criação de novo orçamento
- [ ] Edição de orçamento existente
- [ ] Exclusão de orçamento
- [ ] Filtros por período (mês/ano)
- [ ] Cálculo correto de progresso
- [ ] Comparativo entre orçado e gasto real

## 7. Módulos de Análise
- [ ] Carregamento correto dos gráficos
- [ ] Filtros por período
- [ ] Gráfico de despesas por categoria
- [ ] Gráfico de receitas por categoria
- [ ] Gráfico de evolução mensal
- [ ] Gráfico comparativo receitas x despesas

## 8. Relatórios
- [ ] Geração de relatório mensal
- [ ] Geração de relatório anual
- [ ] Geração de relatório personalizado
- [ ] Exibição correta de dados no relatório
- [ ] Funcionalidade de exportação (PDF, Excel, CSV)

## 9. Configurações do Usuário
- [ ] Edição de perfil
- [ ] Alteração de senha
- [ ] Configuração de preferências
- [ ] Gerenciamento de categorias
- [ ] Exportação de dados
- [ ] Exclusão de conta

## 10. Testes de Integração
- [ ] Fluxo completo: criação de conta > registro de transações > análise
- [ ] Fluxo completo: definição de orçamento > registro de gastos > comparativo
- [ ] Fluxo completo: criação de sonho > adição de valores > conclusão

## 11. Testes de Usabilidade
- [ ] Navegação intuitiva entre as seções
- [ ] Feedback visual para ações do usuário
- [ ] Mensagens de erro claras e informativas
- [ ] Responsividade em diferentes dispositivos
- [ ] Consistência visual em todo o sistema

## 12. Testes de Segurança
- [ ] Proteção de rotas para usuários não autenticados
- [ ] Validação de permissões de acesso
- [ ] Segurança na alteração de senha
- [ ] Proteção contra injeção de SQL
- [ ] Validação de dados de entrada

## Observações e Correções Necessárias
*Registre aqui as observações e correções identificadas durante os testes*
