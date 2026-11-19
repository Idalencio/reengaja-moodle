# Explicação curta

O sistema procura no Moodle quem ainda não enviou uma tarefa que vence nas próximas 24 horas. O acompanhamento faz essa consulta e coloca a solicitação no RabbitMQ. O serviço de notificações recebe a solicitação, envia o e-mail e registra o resultado.

O lembrete traz atividade, prazo e link. Tarefas vencidas, sem prazo, já enviadas, ocultas ou em grupo ficam fora. O rascunho continua pendente. Uma chave com curso, tarefa e aluno impede repetir um envio que já está registrado como concluído. Uma falha temporária gera nova tentativa, até três no total.

Em 19/11, o GitHub Actions aprovou os serviços com Docker, 104 testes e nove cenários de integração. Os registros também preservam o ensaio no Moodle real de 06/11. O repositório já é público. Para concluir a entrega, faltam o vídeo no YouTube e os registros extensionistas reais.
