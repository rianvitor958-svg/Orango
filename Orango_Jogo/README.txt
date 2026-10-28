CAMPO MINADO ORANGO + SENAC

REQUISITOS
- Python 3.10 ou superior
- Conexão com a internet para instalar Flask caso ainda não esteja instalado

COMO EXECUTAR NO WINDOWS / VS CODE
1. Extraia o ZIP.
2. Abra no VS Code a pasta onde estão app.py e requirements.txt.
3. No terminal, execute: python -m pip install -r requirements.txt
4. Inicie: python app.py
5. Abra no Chrome: http://127.0.0.1:5001

IMPORTANTE: Esta versão roda na porta 5001 de propósito para não abrir por engano a versão antiga que ainda esteja rodando na porta 5000. O cabeçalho tem “Conhecer o Orango”; não deve aparecer “Entrar no Orango” nem “Fazer login”.

O banco orango_game.db é criado automaticamente ao iniciar o app e permanece na pasta de app.py. Não apague esse arquivo se quiser preservar os dados.

FUNCIONALIDADES
- Navegação entre Início, Campo Minado, Conquistas, Ranking e Sobre o Orango.
- Tutorial animado exibido na primeira visita, com explicações e botão para abrir novamente em “Como jogar”.
- Campo Minado com três dificuldades, marcação de minas, cinco recompensas e reinício. A primeira casa clicada sempre é segura e abre uma área inicial sem minas nem recompensas adjacentes. As cinco recompensas podem ser encontradas na mesma partida, mas ficam em casas numeradas espalhadas pelo mapa, fora das áreas abertas automaticamente, e as dificuldades têm mais minas.
- Ao encontrar as cinco recompensas na mesma partida, aparece a mensagem “Você ganhou!” e o botão “Ir para o Orango”, que abre https://orango.senac.br/ em uma nova aba.
- Recompensa visual de 20% é ilustrativa e não constitui cupom oficial ou desconto garantido pelo Orango.
- Música de fundo original gerada pelo navegador (Web Audio API), inicia automaticamente no primeiro clique do tabuleiro. O botão de música foi removido; não precisa baixar arquivos de áudio. O navegador exige uma interação do usuário para permitir o som.
- Botões de login removidos. Os links para o Orango levam ao site oficial.
- Logo do Senac em PNG transparente aplicada no cabeçalho, junto ao título do jogo e no rodapé; logo do Orango exibida no cabeçalho e rodapé.
- SQLite persistente com jogadores, histórico, conquistas e relações entre jogador e conquista.
- Apelido local (1 a 24 caracteres), estatísticas e ranking ordenado por pontos, vitórias, partidas e data de cadastro.
- Ranking com medalhas para os três primeiros colocados e botão Excluir. A exclusão pede confirmação e remove também o histórico e as conquistas associadas.
- Página inicial com estatísticas e destaques reais do banco de dados.

OBSERVAÇÕES
- O ranking é local a esta instalação e não se conecta à conta ou aos sistemas internos do Orango.
- A recompensa de 20% é apenas uma representação visual do projeto; não é cupom oficial.
- A exclusão de jogadores é uma função administrativa de demonstração para uso local, não um controle de acesso seguro para produção.
- A pontuação é calculada parcialmente no servidor, mas este jogo local demonstrativo não deve ser tratado como plataforma competitiva resistente a manipulação avançada.

TESTES REALIZADOS NESTA ENTREGA
- Sintaxe Python (py_compile): aprovada.
- Sintaxe JavaScript (node --check): aprovada.
- Estrutura HTML (HTMLParser): aprovada.
- Verificação de que os botões e identificadores de login foram removidos: aprovada.
- Verificação da presença do tutorial e da janela de vitória no HTML: aprovada.

TESTES NÃO REALIZADOS NESTE AMBIENTE
- Não foi possível iniciar e testar as rotas Flask, o banco SQLite pela aplicação ou o comportamento real no navegador, pois Flask não está instalado neste ambiente e não foi possível instalar dependências pela rede. Execute os comandos acima no computador local para verificar a aplicação integrada.
