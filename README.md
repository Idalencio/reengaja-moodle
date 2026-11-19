# Reengaja Moodle

[![Testes e integração](https://github.com/Idalencio/reengaja-moodle/actions/workflows/tests.yml/badge.svg)](https://github.com/Idalencio/reengaja-moodle/actions/workflows/tests.yml)

Serviço de reengajamento de estudantes para Engenharia de Software II, 2026/2.
Dois microsserviços Python consultam o Moodle e enviam lembretes por SMTP, usando RabbitMQ para a comunicação assíncrona.

Equipe: Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo.

Entrega prevista: 20/11/2026. A [conferência final](docs/conferencia_final.md) relaciona os pedidos do professor às evidências e às pendências reais.

## Execução

Requisito: Docker Desktop com Docker Compose v2, iniciado e configurado para contêineres Linux.
Na primeira execução é necessário acesso à internet para baixar as imagens.

1. Baixe o repositório ou clone com `git clone https://github.com/Idalencio/reengaja-moodle.git` e abra a pasta `reengaja-moodle`.
2. No Windows, execute `INICIAR_DEMO.bat`. Alternativamente, abra o terminal nessa pasta e execute:

```sh
docker compose up -d --build
docker compose ps
```

3. Abra [Mailpit](http://localhost:8025). Devem aparecer dois lembretes: Ana e Carla.
4. Execute `TESTAR.bat` ou:

```sh
docker compose run --build --rm testes
```

5. Para parar e conservar o histórico:

```sh
docker compose down
```

O primeiro ciclo acontece assim que o serviço inicia. O intervalo padrão é uma hora.
Para uma demonstração com ciclos de 30 segundos, copie `.env.example` como `.env`, altere
`POLL_INTERVAL_SECONDS=30` e execute novamente `docker compose up -d`.
Não é necessário instalar Python no computador para usar o Compose.

## Demonstração

O serviço `moodle-demo` é um **simulador do contrato REST**, com contas fictícias. Não é o Moodle da instituição.
Ao iniciar o simulador, os prazos são fixados em relação ao horário de início. Se a demonstração ficar aberta
por mais de duas horas, reinicie `moodle-demo` para gerar novos prazos. O histórico de envio continua valendo;
por isso, o reinício não produz novamente lembretes já enviados.

| Estudante / tarefa | Resultado |
| --- | --- |
| Ana: tarefa 501, pendente, vence em 2 horas | Recebe um lembrete |
| Bruno: tarefa 501, já enviada | Não recebe |
| Carla: tarefa 501, rascunho | Recebe um lembrete |
| Tarefa vencida, sem prazo ou para daqui a 48 horas | Ignorada |
| Tarefa em grupo, oculta, restrita, offline ou ainda fechada | Ignorada |
| Repetição do mesmo curso, tarefa e aluno | Não gera novo envio concluído |

Os testes de integração usam endereços com uma etiqueta aleatória e filas próprias. Eles geram **três mensagens adicionais**
por execução: duas iniciais e uma após recuperação de falha. Não confundem esses e-mails com os dois da demonstração normal.

## Consultar execução e resultados

| Recurso | Endereço / comando |
| --- | --- |
| E-mails de teste | http://localhost:8025 |
| RabbitMQ Management | http://localhost:15672 |
| Usuário / senha locais do RabbitMQ | `reengaja` / `demo-local` |
| Estado do acompanhamento | http://localhost:8081/ready |
| Estado das notificações | http://localhost:8082/ready |
| Logs | `docker compose logs -f acompanhamento notificacoes` |
| Resultado dos testes | `test-results/junit.xml` e `test-results/unitarios.txt` |
| Evidência da integração | `evidencias/integracao.json` e arquivos `.eml` |

`/health` informa que o processo HTTP está vivo; `/ready` informa que o acompanhamento concluiu um ciclo
ou que o consumidor se conectou ao broker. O estado do consumidor não comprova disponibilidade do SMTP.

## Estrutura

- `acompanhamento/`: adaptador Moodle, seleção de pendências e publicação.
- `notificacoes/`: consumo, composição de e-mail, SMTP, histórico e auditoria.
- `infra/`: configuração, contrato das mensagens, AMQP, logs e saúde.
- `demo/`: simulador REST para contas fictícias.
- `tests/`: testes automatizados de regras, contrato, adapters, persistência e concorrência.
- `scripts/integration.py`: teste com RabbitMQ e Mailpit reais.
- `docs/`: instalação no Moodle, arquitetura, requisitos, roteiro, extensão e entrega.
- `scripts/verificar_containers.py`: confere os dois serviços, os destinatários e o histórico depois de reiniciar o consumidor.
- `.github/workflows/tests.yml`: inicia a composição, verifica os contêineres e executa a suíte no GitHub Actions.

## Regras e limitações

A janela é `agora < prazo <= agora + 86400 segundos`. O limite de 24 horas está incluído;
o instante exato do vencimento está excluído. Os timestamps Unix são comparados como instantes absolutos.
O e-mail apresenta a data no fuso `America/Sao_Paulo`.

Rascunho ainda não é entrega final. A tentativa mais recente com status `submitted` dispensa o lembrete.
O link usa o ID do **módulo** (`cmid`), que pode ser diferente do ID da tarefa.
Tarefas sem submissão online, com anonimato de autoria ou fora do escopo são excluídas.

O consumidor persiste a chave `curso:tarefa:aluno` no SQLite, armazenado em volume do Docker. Ele confirma
a mensagem no RabbitMQ somente depois do processamento ou da publicação confirmada na fila de retry/falha.
Uma falha temporária permite até três tentativas no total. O intervalo de retry é configurável.
Respostas SMTP 5xx são tratadas como definitivas; mensagens inválidas vão para a fila `.dead`.
Mensagens que vencem aguardando processamento são registradas como `expired`.

**Limite técnico:** SMTP e SQLite não participam de uma mesma transação. Se o processo morrer depois de o SMTP aceitar
o e-mail e antes do commit local, uma redelivery pode gerar duplicata. A chave persistente impede reenvio de solicitações
**já registradas como concluídas**, que é o critério do enunciado. Não há promessa de exactly-once para falhas nessa janela.
O `Message-ID` estável facilita rastreamento, mas não obriga o servidor SMTP a deduplicar.

A situação de entrega é uma fotografia do momento da consulta. Uma submissão feita após a consulta ao Moodle
pode coincidir com um lembrete já enfileirado. Tarefas com regras individuais, grupos, prorrogações ou restrições de seção
precisam ser retiradas do curso monitorado ou validadas previamente com o parceiro.

Não remova os volumes durante o uso: apagar o banco apaga o histórico de idempotência.
O projeto usa um consumidor e disco local. Escalar para múltiplas máquinas exige um banco transacional centralizado.

## Verificação da entrega

O cliente foi testado com o Moodle 5.3 da demonstração oficial: cinco cenários adicionais passaram e dois e-mails chegaram ao Mailpit. Os registros estão em `evidencias/moodle_real_fluxo.json` e `moodle_real_fluxo.log`. O [protocolo do ensaio](docs/teste_moodle_real.md) explica as etapas. A demonstração local padrão continua usando o simulador para não depender dos dados temporários do site público.

O [guia do Moodle](docs/moodle_real.md) descreve como configurar outra instalação. O ambiente definitivo deve ser confirmado com o parceiro.

Em 19/11, o GitHub Actions aprovou a execução com Docker: os dois microsserviços ficaram prontos, Ana e Carla receberam os lembretes e Bruno não recebeu. O reprocessamento e o reinício do consumidor preservaram o total de e-mails. Os 104 testes de unidade/componentes e os nove cenários de integração também passaram em contêineres, sem falhas.

Para conferir os contêineres em uma demonstração nova, com Python 3 instalado no computador:

```sh
docker compose up -d --build --wait --wait-timeout 180
python scripts/verificar_containers.py
docker compose run --build --rm testes
```

O workflow repete essas etapas sem exigir Python no computador da equipe. O arquivo `test-results/execucao_containers.json` só é gerado depois de todas as verificações passarem.

Execução aprovada: https://github.com/Idalencio/reengaja-moodle/actions/runs/44545022348. O artefato `registros-de-testes` contém os logs, `execucao_containers.json`, resultados unitários e evidências da integração. A cópia dos logs e o resumo da execução estão em `evidencias/github_actions_19_11.log` e `evidencias/ci_github.json`. Os 104 testes também passaram localmente em 19/11, com 94% de cobertura.

Para a entrega de 20/11, ficam a publicação do vídeo, o registro do retorno real do parceiro e a conclusão dos relatos individuais. As quatro bases nomeadas estão em `preparacao_extensao/`.

## Material da equipe

- [Pendências e comprovações](docs/pendencias.md)
- [Organização em quatro frentes](docs/organizacao_equipe.md)
- [Roteiro para quatro integrantes](docs/roteiro_4_integrantes.md)
