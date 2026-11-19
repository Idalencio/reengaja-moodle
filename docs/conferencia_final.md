# Conferência dos pedidos do professor

Fonte: projeto_2026_2.pdf, Engenharia de Software II, 2026/2. Revisão de 19/11/2026.
Entrega e apresentação: 20/11/2026. O arquivo cita uma rubrica, mas não traz seus pesos detalhados.

| Pedido e página do enunciado | O que foi implementado ou preparado | Comprovação e situação |
| --- | --- | --- |
| Dois microsserviços, p. 4-6 | Acompanhamento e notificações em processos e Dockerfiles distintos | Dois processos executados e prontos, evidencias/ambiente.json |
| Integração REST com Moodle, p. 7 | Tarefas, matriculados, entregas e consulta complementar de visibilidade | Cliente acompanhamento/moodle.py e ensaio real de 06/11 |
| Consulta a cada hora, configurável, p. 6 | POLL_INTERVAL_SECONDS=3600 e primeiro ciclo ao iniciar | infra/config.py e acompanhamento/__main__.py |
| Pendência nas próximas 24 horas, p. 3, 6 e 8 | Intervalo 0 < prazo - agora <= 86400 | Testes de borda e cenários I01/I02 e M01 |
| Ignorar enviada, vencida e sem prazo, p. 8-9 | Tentativa mais recente e filtros de elegibilidade | tests/test_rules.py, I01/I07 e M03/M04 |
| Uma disciplina, tarefa individual visível, p. 8 | Curso configurado, exclusão de grupos e restrições | Filtros de tarefa e módulo |
| RabbitMQ assíncrono, p. 5 | Mensagens persistentes, filas duráveis e confirmação manual | Integração real I02 a I09 |
| E-mail com nome, prazo e link, p. 2 | Conteúdo texto/HTML e link com cmid | Arquivos EML e testes de composição |
| Não reenviar solicitação concluída, p. 6 e 9 | Chave curso:tarefa:aluno e histórico SQLite persistente | I03/I04, reinício de processo e M02 |
| Falha registrada e nova tentativa, p. 9 | Histórico, fila de espera e até três tentativas | I05/I06/I09 e M05 |
| Contas fictícias e Mailpit, p. 9 | endereços example.test e servidor SMTP local | Três e-mails no ensaio local e dois no ensaio Moodle real |
| Contêineres, p. 4 | Dockerfiles, Compose, dois serviços prontos e histórico preservado após reinício | APROVADO em 19/11 no GitHub Actions, execução 44545022348 |
| Código, guia e registros de testes, p. 10 | Fontes, README, docs e evidências reproduzíveis | Incluídos no pacote |
| Repositório público GitHub, p. 10 | Fontes, documentação, slides e evidências publicados | https://github.com/Idalencio/reengaja-moodle |
| Vídeo da apresentação no YouTube, p. 11 | Slides editáveis, roteiro para quatro pessoas e vídeo de apoio | PENDENTE: gravar/revisar a apresentação do grupo e publicar o link |
| Relatório individual de extensão, p. 12 | Quatro bases nomeadas em preparacao_extensao/ | PENDENTE: cada pessoa registrar suas contribuições e aprendizagens reais |
| Equipe de até quatro pessoas, p. 14 | Os quatro nomes em EQUIPE.md, relatório e apresentação | Identificação preenchida |
| Checkpoints com o parceiro, p. 11 | Formulário e perguntas de validação | PENDENTE: registrar contatos e feedback efetivamente recebidos |

## Limites das comprovações

Em 19/11, o GitHub Actions aprovou quatro verificações Docker, 104 testes de unidade/componentes e nove cenários de integração. O artefato registros-de-testes contém execucao_containers.json e os logs. Os cinco cenários no Moodle real são os registros históricos de 06/11, não uma homologação no Moodle do parceiro. Não há registro de aprovação do parceiro nem medição de impacto educacional.
