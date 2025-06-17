import pygame

LARGURA_TELA = 1000
ALTURA_TELA = 700
TAMANHO_BLOCO = 28
GRID_COLUNAS = 16
GRID_LINHAS_VISIVEIS = 22
GRID_LINHAS_INVISIVEIS = 2
GRID_LINHAS_TOTAL = GRID_LINHAS_VISIVEIS + GRID_LINHAS_INVISIVEIS
LARGURA_JOGO = GRID_COLUNAS * TAMANHO_BLOCO
ALTURA_JOGO = GRID_LINHAS_VISIVEIS * TAMANHO_BLOCO
PAINEL_INFO_LARGURA = 200
ESPACAMENTO_PAINEL = 50
LARGURA_TOTAL_CONTEUDO = LARGURA_JOGO + ESPACAMENTO_PAINEL + PAINEL_INFO_LARGURA
CANTO_SUPERIOR_X = (LARGURA_TELA - LARGURA_TOTAL_CONTEUDO) // 2
CANTO_SUPERIOR_Y = (ALTURA_TELA - ALTURA_JOGO) // 2
PAINEL_INFO_X = CANTO_SUPERIOR_X + LARGURA_JOGO + ESPACAMENTO_PAINEL


PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (128, 128, 128)
COR_FUNDO = (20, 20, 30)

COR_PAINEL_FUNDO_NEON = (28, 30, 40, 230)
COR_PAINEL_BORDA_NEON = (110, 120, 255)
COR_PAINEL_SOMBRA = (10, 10, 15, 150)
COR_TITULO_GAME = (120, 255, 120)
COR_TITULO_OVER = (150, 150, 255)
COR_BOTAO_NEON_HOVER = (180, 190, 255)
COR_GRID = (40, 40, 60)

OURO = (255, 215, 0)
PRATA = (192, 192, 192)
BRONZE = (205, 127, 50)
COR_DESTAQUE_JOGADOR = OURO

COR_BOTAO_MENU = (70, 70, 100)
COR_BOTAO_MENU_HOVER = (100, 100, 140)
COR_TEXTO_MENU = BRANCO
COR_INPUT_FUNDO = (40, 40, 60)
COR_INPUT_BORDA_INATIVA = (100, 100, 140)
COR_INPUT_BORDA_ATIVA = (170, 170, 220)
COR_INPUT_TEXTO = (230, 230, 230)
COR_INPUT_PROMPT = (130, 130, 130)
COR_TEXTO = (230, 230, 230)
COR_PAINEL_FUNDO = (35, 35, 50)
COR_PAINEL_BORDA = (70, 70, 90)
COR_TECLA_HOLD = (60, 60, 80)
COR_OVERLAY_PAUSA = (0, 0, 0, 180)

TEMPO_FIXAR_PECA = 0.3
VELOCIDADES_QUEDA_NIVEL = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.08, 0.06]
ATRASO_DAS, TAXA_ARR = 150, 30
DURACAO_ANIMACAO_LINHA = 0.4
INTERVALO_PISCAR_LINHA = 100

CIANO, AZUL, LARANJA, AMARELO, VERDE, ROXO, VERMELHO = (0, 200, 200), (0, 100, 255), (255, 150, 0), (255, 220, 0), (0, 200, 50), (150, 0, 200), (230, 50, 50)
CORES_TETROMINOS = [CIANO, AZUL, LARANJA, AMARELO, VERDE, ROXO, VERMELHO]
COR_BASE_FANTASMA, ALPHA_COR_FANTASMA = CINZA, 80

FORMA_I = [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)], [(0, 2), (1, 2), (2, 2), (3, 2)], [(1, 0), (1, 1), (1, 2), (1, 3)]]
FORMA_J = [[(0, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (2, 0), (1, 1), (1, 2)], [(0, 1), (1, 1), (2, 1), (2, 2)], [(1, 0), (1, 1), (0, 2), (1, 2)]]
FORMA_L = [[(2, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (1, 2), (2, 2)], [(0, 1), (1, 1), (2, 1), (0, 2)], [(0, 0), (1, 0), (1, 1), (1, 2)]]
FORMA_O = [[(0, 0), (1, 0), (0, 1), (1, 1)]]
FORMA_S = [[(1, 0), (2, 0), (0, 1), (1, 1)], [(1, 0), (1, 1), (2, 1), (2, 2)], [(1, 1), (2, 1), (0, 2), (1, 2)], [(0, 0), (0, 1), (1, 1), (1, 2)]]
FORMA_T = [[(1, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (2, 1), (1, 2)], [(0, 1), (1, 1), (2, 1), (1, 2)], [(1, 0), (0, 1), (1, 1), (1, 2)]]
FORMA_Z = [[(0, 0), (1, 0), (1, 1), (2, 1)], [(2, 0), (1, 1), (2, 1), (1, 2)], [(0, 1), (1, 1), (1, 2), (2, 2)], [(1, 0), (0, 1), (1, 1), (0, 2)]]

TETROMINOS = {
    'I': {'cor': CIANO, 'forma': FORMA_I}, 'J': {'cor': AZUL, 'forma': FORMA_J},
    'L': {'cor': LARANJA, 'forma': FORMA_L}, 'O': {'cor': AMARELO, 'forma': FORMA_O},
    'S': {'cor': VERDE, 'forma': FORMA_S}, 'T': {'cor': ROXO, 'forma': FORMA_T},
    'Z': {'cor': VERMELHO, 'forma': FORMA_Z}
}
DESLOCAMENTOS_JLSTZ = {
    (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)], (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)], (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)], (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)], (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
}
DESLOCAMENTOS_I = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)], (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)], (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)], (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)], (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
}

RECT_GAMEOVER_NOME = pygame.Rect(290, 115, 480, 80)
RECT_GAMEOVER_RANKING = pygame.Rect(140, 220, 520, 350)
RECT_GAMEOVER_STATS = pygame.Rect(680, 220, 230, 210)
RECT_GAMEOVER_BOTAO_REINICIAR = pygame.Rect(375, 595, 250, 55)
RECT_GAMEOVER_BOTAO_MENU = pygame.Rect(375, 655, 250, 55)