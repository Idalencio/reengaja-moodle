# Relatório individual de extensão - Lucas Gallesio

Engenharia de Software II - 2026/2

Projeto: Reengaja Moodle.

Data: 19/11/2026.

## Contexto do projeto

O Reengaja Moodle propõe um apoio ao acompanhamento das atividades escolares. O serviço envia um lembrete por e-mail ao estudante que ainda não entregou uma tarefa com vencimento nas próximas 24 horas. A mensagem apresenta a atividade, o prazo e o link de acesso. A intenção é facilitar a organização das pendências e reduzir a necessidade de contatos manuais.

## Minha participação e aprendizagens

O roteiro da equipe relaciona minha parte à apresentação da proposta e do escopo. Meu foco neste relato é explicar o problema que o serviço procura resolver e como as regras de acompanhamento se relacionam com a rotina de professores e estudantes.

Um ponto que considero importante é a definição dos limites do projeto. A solução acompanha uma disciplina, com tarefas individuais visíveis para toda a turma e um prazo comum. Atividades em grupo e prorrogações individuais ficam fora desse recorte. Essas escolhas ajudam a definir o comportamento esperado e a conferir os resultados.

A mensagem também precisa ser objetiva. Informar somente que existe uma pendência seria pouco útil. O nome da atividade, a data de entrega e o link permitem que o estudante saiba o que precisa fazer e onde acessar a tarefa. Esse cuidado relaciona os requisitos técnicos à utilidade do serviço.

## Resultados observados

Os registros de 19 de novembro mostram 104 testes de unidade e componentes e nove cenários de integração aprovados. A execução com Docker também confirmou o envio para Ana e Carla, a ausência de envio para Bruno e o bloqueio de novas mensagens ao reprocessar solicitações concluídas. Os testes usam contas fictícias e e-mails capturados no Mailpit.

## Relação com a formação e a extensão

Vejo a relação com a prática extensionista na aplicação dos conteúdos da disciplina a uma necessidade do ambiente educacional. O benefício esperado é apoiar o acompanhamento das tarefas. Os resultados técnicos mostram o funcionamento do serviço, enquanto uma mudança na participação dos estudantes precisaria de acompanhamento real. Para minha formação, o projeto reforça a importância de compreender a necessidade atendida antes de ampliar as funcionalidades.

Código e documentação: https://github.com/Idalencio/reengaja-moodle
