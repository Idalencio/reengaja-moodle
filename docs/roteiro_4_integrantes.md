# Roteiro da apresentação

Equipe: Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo.

Tempo sugerido: 6 a 8 minutos de explicação, mais a demonstração. A divisão das falas pode ser ajustada.

## Slide 1 - Lucas Gallesio

Reengajamento no Moodle

Abrir a apresentação identificando o projeto e a equipe. A ideia é ajudar no acompanhamento das tarefas pendentes, enviando um lembrete antes do prazo. A apresentação foi dividida entre Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo. O cenário é uma disciplina com tarefas individuais e prazo comum. Fonte: enunciado, páginas 1 a 4 e 8.

## Slide 2 - Lucas Gallesio

Acompanhamento das pendências

Lucas: O problema apresentado pela disciplina é o trabalho de consultar tarefas e fazer contatos manuais. O lembrete é preventivo e objetivo: nome da atividade, prazo e link. O sistema considera uma disciplina e tarefas individuais visíveis para toda a turma. Entregas em grupo, prorrogações individuais e outros canais ficam fora do escopo. O benefício esperado é reduzir contatos manuais. Ainda não medimos mudança na participação ou na taxa de entregas. Fonte: enunciado, páginas 2, 3 e 8.

## Slide 3 - Pedro Idalencio

Dois microsserviços

Pedro: O Moodle continua sendo o sistema de origem. O acompanhamento usa HTTP e as funções de tarefas, matriculados e entregas. Consultamos também o conteúdo do curso para verificar visibilidade. O token segue no corpo do POST. Depois de concluir a consulta, o acompanhamento publica a solicitação no RabbitMQ. O serviço de notificações consome essa solicitação em outro processo. A fila desacopla consulta e envio: o acompanhamento não precisa aguardar o SMTP. Cada serviço tem seu Dockerfile. Fontes: enunciado páginas 4 a 7; acompanhamento/moodle.py; infra/broker.py.

## Slide 4 - Pedro Idalencio

Seleção de quem recebe

Pedro: A regra é zero menor que prazo menos agora, menor ou igual a 86.400 segundos. O limite de 24 horas entra. O instante do vencimento já fica fora. Consideramos a tentativa mais recente e submitted como entrega final. Rascunho continua pendente. A tarefa precisa estar visível e permitir envio individual. O e-mail usa o cmid, identificador do módulo, que pode ser diferente do ID da tarefa. Se a consulta de entregas falhar, o ciclo não publica uma lista parcial. Fontes: acompanhamento/service.py, tests/test_rules.py e enunciado páginas 8 e 9.

## Slide 5 - Artur Thomé

Repetição e falhas

Artur: O serviço consulta o SQLite antes de enviar. A chave reúne curso, tarefa e aluno. O volume preserva esse registro após reiniciar o consumidor. Uma falha temporária gera um registro e uma publicação na fila de espera. O TTL faz a mensagem voltar para a fila principal. O ACK da original só acontece depois do processamento ou da publicação confirmada da nova tentativa. Testamos uma conexão SMTP recusada e depois o envio com sucesso na segunda tentativa. Há um limite: uma queda depois da aceitação SMTP e antes do commit pode causar duplicata. Fontes: notificacoes/store.py, notificacoes/service.py e infra/broker.py.

## Slide 6 - Artur Thomé

Demonstração do fluxo

Artur: Usar INICIAR_DEMO.bat com o Docker Desktop iniciado. Abrir localhost:8025. Na demonstração nova devem existir dois lembretes: Ana e Carla, sem envio para Bruno. Executar docker compose exec acompanhamento python -m acompanhamento --once. Os logs registram notificacao_duplicate e o total de mensagens não aumenta. Executar TESTAR.bat para mostrar o erro de conexão registrado e o sucesso na segunda tentativa. Se não houver Docker disponível na apresentação, mostrar os arquivos EML e os registros preservados, identificando que são evidências da execução anterior. Não anunciar uma execução ao vivo sem executá-la. Fontes: README.md e evidencias/integracao.json.

## Slide 7 - Vitor Hugo

Critérios de aceite verificados

Vitor: Os 104 testes de unidade e componentes passaram novamente em 16 de novembro. Também passaram nove cenários de integração, usando Moodle simulado, RabbitMQ real e Mailpit real. Os cinco cenários M01 a M05 são o ensaio histórico de 6 de novembro no Moodle real da demonstração oficial, versão 5.3. São ambientes e datas diferentes. A cobertura medida é de 94,3% das instruções incluídas, excluindo pontos de entrada e scripts. Os pontos de entrada também rodaram separadamente e o reinício do consumidor preservou o histórico. Fontes: test-results/junit.xml, coverage.json, evidencias/integracao.json e moodle_real_fluxo.json.

## Slide 8 - Vitor Hugo

Uso com a instituição

Vitor: O projeto atende aos quatro comportamentos exercitados nos testes. A integração pública de demonstração não equivale à homologação no Moodle do parceiro. Precisamos registrar o feedback real, confirmar o ambiente e repetir o aceite se a instalação mudar. A composição Docker tem arquivos e verificação automática preparados, mas esta revisão não conseguiu executar o daemon no ambiente disponível. Também falta publicar os links e completar os relatos com a participação real de cada integrante. Essa distinção evita tratar preparação como comprovação. Fontes: docs/conferencia_final.md e enunciado páginas 10 a 12.

## Perguntas que todos precisam saber responder

| Pergunta | Resposta direta |
| --- | --- |
| Por que usar dois serviços? | Um consulta e identifica a pendência. Outro envia e registra. São processos separados com responsabilidades distintas. |
| Qual parte é síncrona? | A chamada HTTP à API REST do Moodle espera uma resposta. |
| Qual parte é assíncrona? | O acompanhamento publica no RabbitMQ e a notificação processa depois, independentemente. |
| O que é idempotência neste projeto? | Reprocessar uma chave já registrada como enviada não gera outro e-mail. |
| Por que usar cmid no link? | A página mod/assign/view.php espera o ID do módulo do curso. O ID interno da tarefa pode ser outro. |
| Como diferenciar rascunho de entrega? | submitted na tentativa mais recente dispensa o lembrete. draft permanece pendente. |
| E se o SMTP cair? | Registra o erro e tenta de novo após a espera, até três tentativas. |
| E se o consumidor reiniciar? | As mensagens são persistentes e o SQLite fica em volume. O histórico concluído continua bloqueando repetição. |
| Há garantia absoluta de um único e-mail? | Não. SMTP e SQLite não têm transação conjunta. O critério comprovado cobre o que já ficou registrado como concluído. |
| Foi integrado ao Moodle real? | Sim, houve ensaio na demonstração oficial em 06/11. O simulador local mantém a demonstração reproduzível. Não há homologação registrada na instalação do parceiro. |
| O projeto melhorou a participação dos alunos? | Esse é o benefício esperado. Não houve medição de impacto educacional. |
| Os contêineres foram executados? | Nesta revisão, a configuração foi validada, mas o ambiente bloqueou o daemon. O workflow preparado precisa produzir o registro real. |

## Comandos da demonstração

```sh
docker compose up -d --build --wait
docker compose exec acompanhamento python -m acompanhamento --once
docker compose run --build --rm testes
docker compose logs --tail 30 notificacoes
docker compose down
```

Abra http://localhost:8025 para os e-mails. Evite apagar os volumes durante o uso: o histórico fica neles.
