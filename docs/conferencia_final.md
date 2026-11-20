# Conferência da entrega

Referência: projeto_2026_2.pdf, Engenharia de Software II, 2026/2, páginas 4 a 12.

| Item | Onde conferir |
| --- | --- |
| Dois microsserviços | `acompanhamento/` e `notificacoes/`, com Dockerfiles próprios |
| Consulta ao Moodle por REST | `acompanhamento/moodle.py` e `evidencias/moodle_real_fluxo.json` |
| Consulta a cada hora, com intervalo configurável | `POLL_INTERVAL_SECONDS` em `infra/config.py` |
| Tarefas pendentes nas próximas 24 horas | `acompanhamento/service.py` e `tests/test_rules.py` |
| Comunicação por RabbitMQ | `infra/broker.py` e cenários I02 a I09 |
| E-mail com atividade, prazo e link | `notificacoes/mailer.py` e arquivos EML |
| Bloqueio de repetição de envio concluído | `notificacoes/store.py` e cenários I03/I04 |
| Falha registrada e nova tentativa | Cenários I05/I06/I09 |
| Execução em contêineres | GitHub Actions, execução de 19/11, com 104 testes e nove cenários aprovados |
| Código, guia e registros dos testes | README, fontes e `evidencias/` |
| Apresentação | Slides em `entrega/` e roteiro em `docs/` |
| Apresentação gravada | MP4 de 6 min 33 s com as vozes dos quatro integrantes e registros dos testes |
| Vídeo no YouTube | Publicar o MP4 e incluir o link em `EQUIPE.md` |
| Relatório individual de extensão | Um texto por integrante em `preparacao_extensao/` |

[Execução de 19/11](https://github.com/Idalencio/reengaja-moodle/actions/runs/44545022348).

Os testes automáticos usam o simulador REST, RabbitMQ e Mailpit. Os cinco cenários no Moodle da demonstração oficial são do ensaio de 06/11. O projeto não apresenta medição do efeito dos lembretes sobre a participação dos estudantes.
