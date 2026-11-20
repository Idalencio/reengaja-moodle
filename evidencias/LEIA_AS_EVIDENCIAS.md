# Registros dos testes

## Docker em 19/11/2026

O [GitHub Actions](https://github.com/Idalencio/reengaja-moodle/actions/runs/44545022348) aprovou 104 testes de unidade e componentes e nove cenários de integração. Também confirmou os dois serviços prontos, os destinatários da demonstração e o histórico após reiniciar o consumidor.

- `ci_github.json`: resumo e endereço da execução.
- `github_actions_19_11.log`: log completo.
- `unitarios_19_11.xml` e `.txt`: resultado dos testes locais de 19/11.
- O artefato `registros-de-testes`, na execução do Actions, contém `execucao_containers.json`, os logs e os demais resultados.

## Execução local de 16/11/2026

`integracao.json` e `integracao.log` registram nove cenários com simulador REST, RabbitMQ e Mailpit reais. A execução gerou três mensagens: duas iniciais e uma após a recuperação de uma falha SMTP.

`ambiente.json` e `worker-*.log` registram os serviços em processos separados e o reinício do consumidor. Os arquivos `email_*.eml` são exportações das mensagens recebidas no Mailpit, com contas fictícias.

## Moodle em 06/11/2026

`moodle_real_fluxo.json`, `moodle_real_fluxo.log` e `moodle_real_email_*.eml` registram cinco cenários executados na demonstração oficial do Moodle 5.3. O fluxo incluiu REST, fila, SMTP e dois e-mails no Mailpit.

Os arquivos mantêm a data de cada execução. Nenhum desses testes mediu o efeito dos lembretes sobre a aprendizagem ou a participação dos estudantes. Tokens, senhas e cookies não fazem parte dos registros.
