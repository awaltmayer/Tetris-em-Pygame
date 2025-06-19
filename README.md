# Tetrizos

## Desenvolvedor
- **Nome:** Augusto Wolfart Altmayer
- **RA (Registro Acadêmico):** 1138100

---

## Descrição do Jogo

Bem-vindo ao **Tetrizos**! Neste jogo, você é um arquiteto digital com a missão de organizar fluxos de dados caóticos que caem do ciberespaço na forma de blocos coloridos, os "Tetrominós".

Seu objetivo é usar lógica e reflexos rápidos para manipular e encaixar essas peças, formando linhas horizontais completas. Cada linha formada é eliminada, liberando espaço e gerando pontos. Conforme você avança, o fluxo de dados se torna cada vez mais rápido, testando seus limites. Cuidado para não deixar a pilha de blocos chegar ao topo, ou o sistema entrará em colapso (Game Over)!

---

## Funcionalidades Principais

O jogo conta com diversas funcionalidades para uma experiência completa:
- Gameplay clássico de Tetris com sistema de rotação moderno (SRS).
- Mecânicas de **Hold** (guardar peça) e **Ghost Piece** (peça fantasma).
- Níveis de dificuldade que aumentam progressivamente.
- **Tela de Boas-Vindas** detalhada com instruções de jogabilidade e visualização das peças.
- **Histórico de Partidas** que salva e exibe os últimos 5 jogos na tela de Game Over.
- **Log de partidas** salvo no arquivo `log.dat` com pontuação, data e hora.
- **Comandos de Voz** para iniciar ou sair do jogo no menu.
- **Feedback por Voz (TTS)** que anuncia o início e o fim do jogo.
- Efeitos visuais dinâmicos no fundo da tela.

---

## Tecnologias Utilizadas

Este projeto foi desenvolvido utilizando as seguintes tecnologias e bibliotecas Python:
- **Python 3**
- **Pygame:** Biblioteca principal para o desenvolvimento do jogo.
- **SQLite3:** Para o banco de dados que armazena o histórico de partidas.
- **PyInstaller:** Para a criação do arquivo executável.
- **pyttsx3:** Para a funcionalidade de síntese de voz (Text-to-Speech).
- **SpeechRecognition:** Para a funcionalidade de reconhecimento de comandos de voz (Speech-to-Text).

---

## Como Executar

### A partir do código-fonte:
1. Certifique-se de ter o Python 3 instalado.
2. Clone o repositório.
3. Instale as dependências: