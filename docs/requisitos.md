# Requisitos e rastreabilidade

Fonte de escopo: `projeto_2026_2.pdf`, fornecido pela disciplina Engenharia de Software II, 2026/2,
professores José Pedro Schardosim Simão e Júlio Machado.

| ID | Requisito | Implementação | Verificação |
| --- | --- | --- | --- |
| R01 | Dois microsserviços | `acompanhamento` e `notificacoes`, cada qual com Dockerfile e processo próprios | Smoke dos pontos de entrada e arquivos de contêiner |
| R02 | Integração síncrona REST com Moodle | POST em `/webservice/rest/server.php` com token no corpo | Testes do adaptador e ensaio real M01 a M05 no Moodle 5.3 da demonstração oficial |
| R03 | Consulta periódica: padrão 1 hora, intervalo configurável | `POLL_INTERVAL_SECONDS=3600` | Configuração e laço do acompanhamento |
| R04 | Identificar tarefa pendente nas próximas 24 horas | `0 < duedate - now <= 86400` | Testes de limites e I01 |
| R05 | Ignorar tarefa já enviada, vencida ou sem prazo | Status final e filtro de prazo | Testes de regras, I01 e I07 |
| R06 | Uma disciplina e tarefas individuais visíveis a toda turma | `MOODLE_COURSE_ID`, filtro de grupo, visibilidade e restrições | Testes de regras/visibilidade e I01 |
| R07 | Mensageria assíncrona RabbitMQ | Filas duráveis, mensagens persistentes, confirms e ACK manual | I02 a I09 e testes do broker |
| R08 | E-mail com nome, prazo e link | MIME texto/HTML, fuso configurável, link por cmid | Arquivos `.eml`, testes e I02 |
| R09 | Um lembrete por curso, tarefa e aluno | Chave única SQLite persistente | Concorrência, reabertura do banco, I03 e I04 |
| R10 | Registrar falhas e tentar novamente | Auditoria, fila retry com TTL e fila dead | I05, I06, I08 e I09 |
| R11 | Contas fictícias e Mailpit nos testes | Domínio reservado `example.test` e Mailpit sem relay | Integração SMTP e mensagens exportadas |
| R12 | Código-fonte e guia de uso | Diretórios de serviços, README e guias | Pacote técnico |
| R13 | Registro dos testes | JUnit, cobertura, JSON de integração, logs e EML | Diretórios `test-results` e `evidencias` |
| R14 | Repositório público GitHub | Fontes, guia e testes publicados | https://github.com/Idalencio/reengaja-moodle |
| R15 | Apresentação e link YouTube | Slides e vídeo com os quatro integrantes | https://youtu.be/aXw6Iu1j9lQ |
| R16 | Relatório de extensão individual | Quatro textos em `preparacao_extensao/` | Cada integrante confere e entrega o próprio texto |
| R17 | Equipe com 2 a 4 pessoas | Ficha `EQUIPE.md` | Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo |

## Critérios de aceite

| Critério do enunciado | Evidência principal |
| --- | --- |
| 1. Lembrete para tarefa pendente dentro da janela | I01 e I02: Ana e Carla recebem; Carla ainda está em rascunho |
| 2. Nenhum lembrete para enviada ou fora da janela | I01: Bruno e tarefas fora do escopo são excluídos; I07: expiração na fila |
| 3. Reprocessar concluída sem novo envio | I03: republicação; I04: reabertura do armazenamento; teste de concorrência |
| 4. Registro de falha e nova tentativa | I05: conexão SMTP recusada registrada; I06: retorno por TTL e sucesso na segunda tentativa |

Os critérios funcionais foram exercitados com o simulador e em um ensaio complementar com Moodle 5.3 real, registrado em evidencias/moodle_real_fluxo.json. A configuração de outra instalação está descrita em `moodle_real.md`.
