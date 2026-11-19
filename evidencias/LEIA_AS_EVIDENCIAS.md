# Registro dos testes executados

- Data do ensaio local mais recente: 16/11/2026.
- 104 testes automatizados aprovados, sem erros ou falhas.
- Cobertura: 94,3% das instruções medidas em acompanhamento, notificacoes e infra.
- 9 cenários de integração aprovados, sem falhas.
- RabbitMQ 3.12.1 real, Mailpit 1.27.4 real e Python 3.12.14.
- Moodle: simulador HTTP do contrato REST, com contas fictícias.
- Dois microsserviços executados em processos separados.
- Reinício real do consumidor: duas duplicatas ignoradas, sem novo e-mail.
- Docker Compose v2.39.4: configuração validada; execução de contêineres não realizada neste ambiente.
- Homologação no Moodle institucional não realizada por falta de acesso autorizado.

O teste de integração injeta uma falha real de conexão SMTP em uma porta local fechada.
O retry e o retorno por TTL ocorrem no RabbitMQ real. O envio posterior chega ao Mailpit por SMTP.

As mensagens EML são exportações dos e-mails efetivamente recebidos, sem encaminhamento externo.
Os endereços usam o domínio reservado example.test e uma etiqueta aleatória de execução.

Arquivos principais: integracao.json, integracao.log, ambiente.json, email_*.eml,
worker-*.log, ../test-results/junit.xml e ../test-results/coverage.json.

Os testes com mocks estão identificados no código da suíte de unidade/componentes.
O script scripts/integration.py usa conexões HTTP, AMQP e SMTP reais contra o ambiente descrito.

## Ensaio histórico com Moodle real

Em 06/11/2026, das 15:24 às 15:27, cinco cenários adicionais passaram no Moodle 5.3 da demonstração oficial. O fluxo incluiu leitura REST, publicação AMQP, consumo, SMTP e auditoria. Dois e-mails foram capturados. Ver moodle_real_fluxo.json, moodle_real_fluxo.log e moodle_real_email_*.eml. Os tokens não fazem parte do pacote.

O ensaio com Moodle real foi preservado e não é uma execução nova de 16/11. A configuração Docker foi novamente validada, mas a criação do socket do daemon foi bloqueada pelo ambiente. O workflow e scripts/verificar_containers.py estão preparados para produzir a evidência de execução dos contêineres quando essa etapa for realizada.

## Execução Docker de 19/11/2026

O GitHub Actions aprovou os dois serviços em contêineres, o envio para Ana e Carla, o bloqueio de repetição e a persistência após reiniciar o consumidor. Na mesma execução passaram 104 testes e nove cenários de integração. A execução completa está em https://github.com/Idalencio/reengaja-moodle/actions/runs/44545022348. O resumo ci_github.json e o arquivo github_actions_19_11.log preservam essa comprovação. O artefato registros-de-testes da execução inclui execucao_containers.json e os demais registros.
