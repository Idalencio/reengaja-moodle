# Reengaja Moodle

[![Testes](https://github.com/Idalencio/reengaja-moodle/actions/workflows/tests.yml/badge.svg)](https://github.com/Idalencio/reengaja-moodle/actions/workflows/tests.yml)

Trabalho de Engenharia de Software II, 2026/2.

**Equipe:** Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo.

O projeto envia um lembrete por e-mail para quem ainda não entregou uma tarefa do Moodle que vence nas próximas 24 horas. O e-mail contém o nome da atividade, o prazo e o link de acesso.

## Como executar

É necessário ter o Docker Desktop iniciado, com contêineres Linux e Docker Compose v2. Na primeira execução, as imagens são baixadas da internet.

```sh
git clone https://github.com/Idalencio/reengaja-moodle.git
cd reengaja-moodle
docker compose up -d --build --wait --wait-timeout 180
```

No Windows, também é possível abrir `INICIAR_DEMO.bat`.

Abra o [Mailpit](http://localhost:8025) para conferir os e-mails. Na demonstração inicial, Ana e Carla recebem um lembrete. Bruno já entregou a atividade e não recebe.

Para executar os testes:

```sh
docker compose run --build --rm testes
```

No Windows, use `TESTAR.bat`. Para encerrar, execute `docker compose down` ou abra `PARAR.bat`. Os volumes mantêm o histórico entre as execuções.

## Funcionamento

- `acompanhamento/` consulta tarefas, matrículas e entregas pela API REST do Moodle.
- `notificacoes/` recebe as solicitações da fila, envia o e-mail e registra o resultado.
- `infra/` reúne a configuração, a comunicação com o RabbitMQ e o formato das mensagens.
- `demo/` simula as respostas da API para a demonstração local.
- `tests/` e `scripts/integration.py` verificam as regras e o fluxo completo.

A consulta acontece ao iniciar e se repete a cada hora. Para mudar o intervalo, copie `.env.example` para `.env` e ajuste `POLL_INTERVAL_SECONDS`.

A demonstração usa contas fictícias, um simulador REST, RabbitMQ e Mailpit. Para conectar outra instalação do Moodle, siga o [guia de configuração](docs/moodle_real.md).

## Regras principais

A janela de envio é `agora < prazo <= agora + 86400`. Tarefas sem prazo, vencidas, já enviadas ou fora do escopo são ignoradas. Um rascunho continua pendente.

Cada lembrete é identificado por curso, tarefa e estudante. O SQLite guarda o histórico e bloqueia outro envio quando essa identificação já está registrada como concluída. Uma falha temporária permite até três tentativas no total.

O SMTP e o banco fazem operações separadas. Uma queda depois da aceitação do e-mail e antes do registro no banco ainda pode causar repetição. Outros detalhes estão em [arquitetura](docs/arquitetura.md).

## Endereços locais

| Serviço | Endereço |
| --- | --- |
| Mailpit | http://localhost:8025 |
| RabbitMQ | http://localhost:15672 |
| Acompanhamento | http://localhost:8081/ready |
| Notificações | http://localhost:8082/ready |

O acesso local do RabbitMQ é `reengaja` / `demo-local`. Para ver os logs, use `docker compose logs -f acompanhamento notificacoes`.

## Testes

Em 19/11/2026, passaram 104 testes de unidade e componentes e nove cenários de integração em contêineres. A verificação também confirmou os destinatários, o bloqueio de repetição e o histórico após reiniciar o consumidor.

[Resultado da execução no GitHub Actions](https://github.com/Idalencio/reengaja-moodle/actions/runs/44545022348).

Os registros estão em `evidencias/`. Os testes de integração criam três e-mails com endereços identificados por execução, além dos dois e-mails da demonstração inicial.

O projeto também tem cinco cenários registrados na demonstração oficial do Moodle em 06/11. Os ambientes e os arquivos de cada execução estão descritos em [registros de testes](evidencias/LEIA_AS_EVIDENCIAS.md).

## Documentação

- [Relatório técnico](entrega/Relatorio_Tecnico_Reengaja_Moodle.pdf)
- [Apresentação](entrega/Apresentacao_Reengaja_Moodle.pdf)
- [Roteiro da equipe](docs/roteiro_4_integrantes.md)
- [Publicação do vídeo com os quatro integrantes](docs/publicacao_video.md)
- [Requisitos](docs/requisitos.md)
- [Relatórios individuais](docs/extensao_individual.md)
- [Entrega no Moodle](docs/entrega.md)
