# Relatório individual de extensão - Vitor Hugo

Engenharia de Software II - 2026/2

Projeto: Reengaja Moodle.

Data: 19/11/2026.

## Contexto do projeto

O Reengaja Moodle propõe lembretes por e-mail para tarefas pendentes que vencem nas próximas 24 horas. A solução utiliza dois microsserviços, com uma fila entre a consulta das pendências e o envio das mensagens. Além de implementar esse fluxo, o trabalho precisa demonstrar os comportamentos definidos no enunciado e reunir registros que permitam conferir os resultados.

## Minha participação e aprendizagens

O roteiro da apresentação reserva minha parte aos critérios de aceite, às evidências dos testes e à relação do projeto com seu uso. Meu foco neste relato é analisar o que cada verificação demonstra e por que a documentação precisa identificar o ambiente e a data da execução.

Os testes de unidade e componentes verificam regras e partes do sistema. Os cenários de integração acompanham a comunicação entre a consulta, a fila, o processamento e o e-mail. Já a execução com Docker verifica se os serviços conseguem iniciar e funcionar na composição preparada para a demonstração. Cada etapa responde a uma questão diferente.

Considero importante avaliar os resultados além da quantidade de testes. Os quatro critérios são enviar o lembrete na janela correta, ignorar entregas concluídas ou fora do prazo, bloquear um novo envio ao reprocessar uma solicitação concluída e registrar falhas com nova tentativa. A documentação relaciona esses critérios aos casos executados.

## Resultados observados

Em 19 de novembro, o GitHub Actions aprovou 104 testes de unidade e componentes e nove cenários de integração em contêineres. A verificação também confirmou os dois serviços prontos, os destinatários esperados e a persistência após reiniciar o consumidor. O projeto preserva ainda cinco cenários históricos na demonstração oficial do Moodle, identificados separadamente dos testes com origem simulada.

## Relação com a formação e a extensão

Para minha formação, o projeto destaca a importância de demonstrar uma afirmação com evidências. Um teste técnico aprovado mostra um comportamento do sistema, enquanto o efeito sobre a participação dos estudantes exige acompanhamento de uso. Essa distinção é relevante para a prática extensionista, porque permite apresentar o benefício esperado sem confundi-lo com um resultado educacional já medido. Os registros também facilitam a apresentação e a compreensão do trabalho por outras pessoas.

Código e documentação: https://github.com/Idalencio/reengaja-moodle
