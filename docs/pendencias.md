# Fechamento da entrega

Revisão: 19/11/2026. Data prevista para apresentação: 20/11/2026.

| Ação restante | Como concluir | Onde registrar |
| --- | --- | --- |
| Comprovar contêineres | Em uma demonstração nova, executar docker compose up -d --build --wait, python3 scripts/verificar_containers.py e docker compose run --build --rm testes. O workflow faz as mesmas verificações no GitHub | test-results/execucao_containers.json, logs e resultado do workflow |
| Publicar apresentação | Usar slides e roteiro, revisar a gravação e publicar no YouTube | EQUIPE.md, com URL do vídeo |
| Registrar a prática extensionista | Anotar o contato real, o retorno do parceiro e os ajustes decorrentes | docs/validacao_parceiro.md |
| Finalizar os relatos | Cada integrante completar sua participação e reflexão | preparacao_extensao/ |

Código, guias, quatro nomes, matriz de requisitos, slides, roteiro e registros técnicos estão no pacote. A configuração Compose passou pela validação sintática. A execução nativa aprovou 104 testes de unidade/componentes e nove cenários de integração em 16/11. O ensaio com Moodle real de 06/11 continua preservado.

O repositório público está em https://github.com/Idalencio/reengaja-moodle. Os 104 testes de unidade/componentes passaram novamente em 19/11, com cobertura total de 94%. A publicação dos fontes aciona a verificação Docker em https://github.com/Idalencio/reengaja-moodle/actions.

O ambiente deste ensaio impediu a criação do socket necessário ao Docker. Esse bloqueio não comprova defeito no projeto, mas também não permite declarar os contêineres testados.
