# Ensaio com Moodle real

Em 06/11/2026, das 15:24 às 15:27 (America/Sao_Paulo), o cliente do projeto foi conectado à demonstração oficial do Moodle 5.3 em https://sandbox.moodledemo.net/.

O ensaio usou contas fictícias do ambiente de demonstração, duas atividades próprias e o curso 2. O RabbitMQ 3.12.1 e o Mailpit 1.27.4 foram executados nativamente. Nenhum e-mail foi encaminhado para um servidor externo.

## Preparação

1. Acesso de professor à API, com as quatro funções de leitura utilizadas pelo acompanhamento.
2. Uma atividade individual com texto online e prazo de duas horas, identificada com prefixo REENGAJA-TESTE.
3. Conta fictícia de aluno matriculada no curso.
4. Filas exclusivas da execução, banco SQLite próprio e Mailpit sem relay.
5. Conferência do fuso: o site usa Australia/Perth; os prazos foram lidos da API como timestamps Unix.

## Resultados

| Caso | Ação | Resultado |
| --- | --- | --- |
| M01 | Consultar a atividade pendente, publicar no RabbitMQ e processar | Primeiro e-mail recebido no Mailpit |
| M02 | Republicar a mesma solicitação concluída | Total permaneceu em um e-mail |
| M03 | Alterar o prazo da atividade para mais de 24 horas | O acompanhamento deixou de selecionar a pendência |
| M04 | Restaurar o prazo, salvar e submeter o texto pela conta fictícia | A API retornou submitted e nenhum novo lembrete foi selecionado |
| M05 | Criar outra atividade pendente, provocar recusa SMTP e processar após o TTL | Falha registrada e segundo e-mail recebido na tentativa 2 |

O primeiro evento teve chave 2:2:4. O evento do teste de recuperação teve chave 2:3:4. Esses identificadores pertencem ao ensaio registrado, não a uma instalação permanente.

## Evidências

- evidencias/moodle_real_fluxo.json: cinco casos, chamadas da API, IDs, horários e auditoria.
- evidencias/moodle_real_fluxo.log: saída da execução.
- evidencias/moodle_real_email_1.eml e moodle_real_email_2.eml: mensagens recebidas.

O ensaio realizou 22 chamadas HTTP à API, incluindo as leituras do acompanhamento e a submissão feita pela conta fictícia. A submissão foi uma ação de preparação do teste, usando mod_assign_save_submission e mod_assign_submit_for_grading na conta do aluno; os microsserviços de produção continuam fazendo somente leituras no Moodle. Tokens, senhas e cookies não estão incluídos no pacote.

## Como repetir em outra instalação

Configure MOODLE_URL, MOODLE_TOKEN e MOODLE_COURSE_ID com o acesso autorizado e use contas fictícias. Siga docs/moodle_real.md para preparar as atividades e repetir os critérios. Para conferir somente as leituras, execute:

```sh
python scripts/verificar_moodle.py
```

Esse comando requer Python 3.12, as dependências de requirements.txt e variáveis de ambiente configuradas. Na execução direta, o arquivo .env não é carregado automaticamente; use as variáveis do sistema ou MOODLE_TOKEN_FILE. O script de leitura não envia e-mails e não valida sozinho o fluxo completo. Para o fluxo, execute acompanhamento e notificações e confira as mensagens e a auditoria.

A demonstração pública do Moodle é reiniciada a cada hora. Os IDs e os tokens utilizados neste ensaio são temporários. A demonstração local do projeto continua usando o simulador para ser repetível sem depender desse site.

O ensaio de 06/11 usou serviços nativos. A execução com contêineres e simulador passou em 19/11; o registro está em `evidencias/ci_github.json`.
