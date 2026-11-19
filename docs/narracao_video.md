# Narração do vídeo de apoio

Narração sintética para revisão. O roteiro do grupo está em roteiro_4_integrantes.md.

## Parte 1

Este vídeo de apoio apresenta o serviço de reengajamento integrado ao Moodle, do projeto de Engenharia de Software dois. A equipe é formada por Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo. O objetivo é enviar lembretes de tarefas pendentes antes do prazo de entrega.

## Parte 2

O problema é o trabalho de acompanhar as pendências e fazer contatos manuais. O serviço identifica quem ainda não enviou uma atividade que vence nas próximas vinte e quatro horas. O e-mail informa o nome da tarefa, o prazo e o link para abrir a atividade no Moodle. O escopo é uma disciplina, com tarefas individuais visíveis e prazo comum. Ainda não foi medido o efeito dos lembretes na participação dos estudantes.

## Parte 3

A aplicação tem dois microsserviços. O acompanhamento consulta o Moodle por uma API REST. Ele lê as tarefas, os estudantes matriculados e as entregas. Quando encontra uma pendência, publica uma solicitação no Rabbit MQ. O serviço de notificações consome a fila, envia o e-mail por SMTP e registra o resultado. A consulta ao Moodle espera uma resposta. A fila permite que o envio aconteça depois, em outro processo.

## Parte 4

No exemplo, Ana ainda não enviou a tarefa e recebe o lembrete. Bruno já enviou e não recebe. Carla salvou somente um rascunho, então continua pendente e recebe. A janela inclui uma tarefa que vence exatamente em vinte e quatro horas. Uma tarefa já vencida, sem prazo ou com mais de vinte e quatro horas fica fora. A tentativa mais recente define se a entrega foi concluída.

## Parte 5

Cada solicitação tem uma chave formada por curso, tarefa e aluno. O histórico fica no SQLite e impede repetir um envio que já está registrado como concluído. Quando ocorre uma falha temporária, o erro é registrado e a mensagem segue para uma fila de espera. Depois ela volta para processamento, até três tentativas no total. Mensagens inválidas e falhas definitivas ficam em outra fila. Existe um limite técnico: uma queda entre a aceitação pelo SMTP e a gravação no banco ainda pode causar duplicata.

## Parte 6

A demonstração usa contas fictícias e o Mailpit para receber os e-mails localmente. Ao iniciar os serviços, Ana e Carla devem receber um lembrete, sem envio para Bruno. Repetir a consulta deve registrar duplicatas sem aumentar o total de mensagens. O teste de falha usa uma conexão SMTP recusada. O erro fica no histórico e, na segunda tentativa, a mesma solicitação chega ao Mailpit com sucesso. Os arquivos de evidência permitem conferir o resultado.

## Parte 7

Em dezesseis de novembro, passaram cento e quatro testes de unidade e componentes e nove cenários de integração. O ambiente local usou origem Moodle simulada, Rabbit MQ real e Mailpit real. Os cinco cenários adicionais com Moodle real pertencem ao ensaio de seis de novembro, na demonstração oficial da versão cinco ponto três. Os registros comprovam os quatro critérios: envio dentro da janela, exclusão de tarefa enviada ou fora do prazo, bloqueio de repetição e recuperação de falha.

## Parte 8

A instalação definitiva precisa ser confirmada com o parceiro, incluindo o curso, as permissões e o remetente dos e-mails. A configuração Docker foi validada, mas este ambiente bloqueou a inicialização do daemon. O workflow preparado deve comprovar a execução dos contêineres. Para fechar a entrega de vinte de novembro, faltam os links públicos, o registro do retorno real do parceiro e os relatos individuais com a participação de cada pessoa. O pacote inclui código, guias, testes, slides editáveis e roteiro para o grupo.
