# Instalação com uma instância Moodle real

## Preparar o curso e as permissões

Este procedimento deve ser feito por um administrador autorizado em uma instância de homologação.
O pacote inclui testes com simulador e um ensaio complementar com Moodle 5.3 real da demonstração oficial. O protocolo está em teste_moodle_real.md. Credenciais de uma instalação institucional não foram fornecidas.

1. Escolha uma disciplina com tarefas individuais, prazo único e sem prorrogações individuais.
   Confirme que todos os estudantes podem visualizar as tarefas e suas seções. Não use atividades em grupo,
   restrições por grupo/nota/perfil, tarefas anônimas ou conteúdos cujo acesso varia entre estudantes.
2. Habilite web services em Administração do site > Recursos avançados.
3. Habilite o protocolo REST em Servidor > Web services > Gerenciar protocolos.
4. Crie um usuário técnico e matricule-o somente no curso necessário, com permissões de leitura adequadas.
5. Cadastre um serviço externo habilitado, restrito a usuários autorizados, com:

| Função | Necessidade |
| --- | --- |
| `mod_assign_get_assignments` | IDs, nomes, prazos e configurações das tarefas |
| `core_enrol_get_enrolled_users` | Estudantes ativos, filtrados por `mod/assign:submit`, e dados de contato |
| `mod_assign_get_submissions` | Status da tentativa mais recente |
| `core_course_get_contents` | Visibilidade do módulo e restrições de acesso disponíveis na API |

6. Confira as capacidades na **Documentação da API da própria instalação**. Na referência Moodle 4.5 consultada,
   os filtros de matrículas exigem `moodle/role:review` e `moodle/course:enrolreview`.
   Também devem ser conferidas as capacidades de REST, leitura dos participantes, visualização de tarefas,
   consulta de entregas e acesso a e-mails. As políticas de privacidade podem omitir o campo `email`.
7. Autorize o usuário técnico nesse serviço, gere o token correspondente e, se aplicável, restrinja IP e validade.
8. Confirme que a capacidade `mod/assign:submit` no curso seleciona apenas o público estudantil pretendido,
   incluindo os papéis personalizados da instituição. Não dependa do nome fixo de um papel chamado "student".

As três funções principais vêm do enunciado. A quarta é uma leitura complementar e não altera o Moodle.
Na referência consultada, `mod_assign_get_assignments` não devolve uma propriedade geral `visible` da atividade.

## Configurar

Copie `.env.example` para `.env`. Ajuste `MOODLE_URL` para a URL base real com HTTPS, sem
`/webservice/rest/server.php` no final, configure `MOODLE_TOKEN` e `MOODLE_COURSE_ID`.
O ID é o número em `course/view.php?id=...`.

Mantenha `SMTP_HOST=mailpit` durante a homologação. Assim os lembretes ficam no capturador de testes.
Para executar apenas a infraestrutura e os microsserviços, sem iniciar o simulador:

```sh
docker compose up -d --build rabbitmq mailpit acompanhamento notificacoes
docker compose logs -f acompanhamento notificacoes
```

O token vai no corpo POST e não aparece na URL ou nos logs da aplicação.
O `.env` não deve ser versionado. A configuração também admite `MOODLE_TOKEN_FILE`, `AMQP_URL_FILE` e
`SMTP_PASSWORD_FILE` para execução por ambiente com arquivos de segredo montados.
Essas variáveis de arquivo devem ser adicionadas ao ambiente do contêiner quando essa alternativa for usada.

## Homologar os quatro critérios no Moodle real

1. Crie contas fictícias A, B e C e matricule-as na disciplina.
2. Crie uma tarefa individual que vença em duas horas. A permanece sem envio; B envia definitivamente; C salva rascunho.
3. Crie tarefas de controle: sem prazo, vencida, para depois de 24 horas e oculta.
4. Execute um ciclo do acompanhamento e confira que somente A e C recebem lembretes no Mailpit.
5. Execute outro ciclo e reinicie o consumidor: o total de mensagens concluídas para a mesma chave deve permanecer igual.
6. Interrompa temporariamente o Mailpit ou configure uma porta SMTP fechada. Registre `notificacao_retry` e a auditoria.
   Restaure o destino antes do vencimento e confira `notificacao_sent` com duas tentativas.
7. Registre a versão do Moodle, configurações, horários, resultado, observações e evidências sem dados reais de estudantes.

Se o e-mail não vier na resposta, o estudante será ignorado com `dados_de_contato_invalidos`.
Se a consulta de entregas falhar ou retornar warnings, o ciclo será interrompido. Isso evita presumir
que uma falha de leitura significa que ninguém enviou a atividade.

## SMTP institucional

Use a conta autorizada pela instituição, `SMTP_SECURITY=starttls` ou `ssl`, porta correspondente,
usuário e senha de aplicação quando exigidos. O modo `none` destina-se ao Mailpit local sem autenticação.
Confirme remetente, política de contatos e destinatários antes de trocar o capturador pelo servidor real.
Não publique credenciais em repositório público.

## Diagnóstico

| Sintoma | Verificação |
| --- | --- |
| `ciclo_falhou` com `MoodleError` | Serviço externo, token, funções, matrícula técnica, permissões e documentação da instância |
| `estudante_ignorado` | Campo email ausente/inválido ou nome/título inválido |
| Nada na fila | Prazo, horário do servidor, visibilidade, grupo, entrega já finalizada |
| `consumidor_reconectando` | RabbitMQ saudável e `AMQP_URL` compatível com usuário e senha |
| `notificacao_retry` | Host, porta e disponibilidade do SMTP |
| `notificacao_dead` | Erro definitivo ou três tentativas; consultar audit e fila `.dead` |
| Mudança de TTL gera `PRECONDITION_FAILED` | A fila existente mantém os argumentos antigos; drene e migre para outro `QUEUE_PREFIX` |
| Alterar senha do RabbitMQ não funciona | Usuário já persistido no volume; ajuste a senha no broker e a AMQP_URL de forma coordenada |

Não apague volumes para "corrigir" problemas em um ambiente que precisa preservar o histórico.
