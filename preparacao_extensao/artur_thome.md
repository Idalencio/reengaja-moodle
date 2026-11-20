# Relatório individual de extensão - Artur Thomé

Engenharia de Software II - 2026/2

Projeto: Reengaja Moodle.

Data: 19/11/2026.

## Contexto do projeto

O Reengaja Moodle envia um lembrete ao estudante que ainda não concluiu uma tarefa com vencimento nas próximas 24 horas. O acompanhamento consulta as pendências e publica as solicitações em uma fila. O serviço de notificações recebe essas mensagens, prepara o e-mail e registra o resultado. O objetivo é apoiar o acompanhamento das atividades com uma comunicação objetiva.

## Minha participação e aprendizagens

No roteiro da equipe, minha parte reúne a explicação das notificações e da demonstração dos e-mails. Neste relato, concentro minha análise no que acontece depois que uma solicitação chega à fila: o envio, o registro do resultado e o tratamento das falhas.

Uma mensagem pode aparecer novamente durante o processamento. Por isso, cada lembrete usa uma identificação formada pelo curso, pela tarefa e pelo estudante. O histórico em SQLite permite reconhecer um envio já concluído e impedir outra mensagem para a mesma solicitação. Esse histórico precisa permanecer disponível após reiniciar o consumidor.

Também considero importante prever a indisponibilidade do servidor de e-mail. Uma falha temporária é registrada e a solicitação aguarda uma nova tentativa, com limite de três no total. O SMTP e o banco realizam ações separadas: uma queda após a aceitação do e-mail e antes do registro local ainda pode causar uma repetição. Esse limite ajuda a compreender o alcance da solução.

## Resultados observados

Os testes de integração registram uma falha de conexão SMTP e o envio com sucesso na segunda tentativa após a recuperação. A execução com Docker de 19 de novembro confirmou a preservação do histórico após reiniciar o consumidor. Na mesma execução, passaram 104 testes de unidade e componentes e nove cenários de integração. O Mailpit permite conferir os e-mails usando contas fictícias.

## Relação com a formação e a extensão

Para minha formação, essa parte do projeto mostra que o envio de uma mensagem envolve mais do que montar seu conteúdo. É preciso registrar o resultado e decidir como agir diante de uma falha. No contexto educacional, esses cuidados ajudam a evitar contatos repetidos e a tornar o acompanhamento mais previsível. A prática extensionista aparece na relação entre essas decisões técnicas e a rotina de quem utiliza o serviço.

Código e documentação: https://github.com/Idalencio/reengaja-moodle
