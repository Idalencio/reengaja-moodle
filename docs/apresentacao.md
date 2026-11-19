# Apresentação de 20/11

O objetivo é explicar a solução, demonstrar os quatro critérios de aceite e apresentar as evidências. Os oito slides estão em entrega/ e as falas nomeadas estão em roteiro_4_integrantes.md.

## Ordem para mostrar

1. Explicar a proposta: lembrar o aluno de uma tarefa pendente que vence em até 24 horas.
2. Mostrar a função de cada serviço e a fila entre eles.
3. Mostrar os casos de Ana, Bruno e Carla.
4. Explicar o bloqueio de repetição e o teste de falha SMTP.
5. Mostrar os resultados no Moodle real e encerrar com a execução em contêineres e o retorno do parceiro.

O arquivo explicacao_curta.md contém uma fala de aproximadamente um minuto. O vídeo tem narração sintética de apoio.

## Demonstração

Inicie com `docker compose up -d --build` e abra http://localhost:8025.
Ana e Carla devem receber um lembrete; Bruno já enviou a tarefa.

Repita o acompanhamento com:

```sh
docker compose exec acompanhamento python -m acompanhamento --once
```

O consumidor deve registrar `notificacao_duplicate` para os envios concluídos, sem outro e-mail para a mesma chave.

Para os cenários de integração:

```sh
docker compose run --build --rm testes
```

Esses testes geram três mensagens próprias, com endereços etiquetados, além das mensagens da demonstração normal.

## Perguntas possíveis

**Já está conectado ao Moodle?**
Sim. O fluxo foi testado no Moodle 5.3 da demonstração oficial, com cinco cenários aprovados. Os arquivos moodle_real_fluxo.json, moodle_real_fluxo.log e os e-mails EML registram esse teste. A demonstração local padrão continua usando o simulador; o ambiente definitivo deve ser combinado com o parceiro.

**Por que dois serviços?**
Um consulta as pendências e o outro cuida do envio. A fila permite que o envio aconteça depois da consulta e que os serviços sejam reiniciados separadamente.

**Como evita e-mail repetido?**
O banco guarda uma chave por curso, tarefa e aluno. Se o envio já terminou e está registrado, a repetição é ignorada. O banco precisa ser preservado entre os reinícios.

**O que acontece se o e-mail falhar?**
A falha é registrada e a mensagem volta para outra tentativa após o TTL. O limite é de três tentativas. Erros definitivos e mensagens inválidas vão para a fila de falhas.

**O que falta?**
Rodar o Compose no destino e registrar o retorno do parceiro e o ambiente definitivo. Depois, preparar os links e documentos da entrega final.
