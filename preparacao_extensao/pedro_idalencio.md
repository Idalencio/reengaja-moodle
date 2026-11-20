# Relatório individual de extensão - Pedro Idalencio

Engenharia de Software II - 2026/2

Projeto: Reengaja Moodle.

Data: 19/11/2026.

## Contexto do projeto

O Reengaja Moodle foi organizado para enviar lembretes a estudantes com tarefas pendentes próximas do prazo. A solução consulta o Moodle, identifica atividades que vencem nas próximas 24 horas e encaminha as solicitações de e-mail para outro serviço. O projeto relaciona integração de sistemas, microsserviços e comunicação por filas a uma necessidade de acompanhamento educacional.

## Minha participação e aprendizagens

Minha participação se concentrou no acompanhamento do desenvolvimento e na organização da entrega. Procurei conferir a integração com o Moodle e a adequação aos requisitos do professor. Também criei o repositório público e encaminhei a organização dos materiais. No roteiro da equipe, minha parte aborda a integração e a seleção dos estudantes que recebem o lembrete.

O ponto central dessa parte é transformar os dados consultados em uma decisão correta. O acompanhamento precisa considerar tarefas, matrículas e entregas. Uma atividade já enviada dispensa o lembrete, mas um rascunho permanece pendente. A janela inclui o limite de 24 horas e exclui o instante do vencimento.

A API REST e a fila cumprem funções diferentes. A consulta ao Moodle espera uma resposta. Depois, a solicitação é publicada no RabbitMQ para que o serviço de notificações faça o processamento. Essa separação ajuda a compreender como cada serviço assume uma responsabilidade sem depender de uma execução única.

## Resultados observados

A execução de 19 de novembro aprovou os serviços com Docker, 104 testes de unidade e componentes e nove cenários de integração. Os registros conferem a seleção dos destinatários, as repetições e a recuperação de falhas. O repositório reúne o código, as instruções de uso e as evidências desses resultados.

## Relação com a formação e a extensão

Para minha formação, a organização do projeto destaca a importância de conferir os requisitos e apresentar evidências do que foi desenvolvido. Na prática extensionista, a integração só tem sentido quando atende a uma necessidade de uso. Neste caso, o lembrete procura apoiar a organização das tarefas e o acompanhamento do professor. A experiência também mostra como uma decisão aparentemente pequena, como diferenciar rascunho de entrega final, altera quem recebe a mensagem.

Código e documentação: https://github.com/Idalencio/reengaja-moodle
