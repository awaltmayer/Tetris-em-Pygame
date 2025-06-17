import pygame
import random
import time
import os
import math
import config
from player import Peca
import database
from widgets import TextInputBox

class Tetris:
    def __init__(self, tela):
        self.tela = tela
        self.grid = self.criar_grid_vazio()
        
        try:
            self.font_principal = pygame.font.Font("recursos/font.ttf", 36)
            self.font_secundaria = pygame.font.Font("recursos/font.ttf", 28)
            self.font_placar = pygame.font.Font("recursos/font.ttf", 22)
        except FileNotFoundError:
            self.font_principal = pygame.font.Font(None, 42)
            self.font_secundaria = pygame.font.Font(None, 34)
            self.font_placar = pygame.font.Font(None, 28)
        
        try:
            self.font_pixel = pygame.font.Font("recursos/pixel_font.ttf", 72)
        except FileNotFoundError:
            print("AVISO: 'pixel_font.ttf' não encontrada. Usando fonte padrão para o título.")
            self.font_pixel = pygame.font.Font(None, 80)

        self.img_borda_esq = self.carregar_imagem("borda_esquerda.png", (config.TAMANHO_BLOCO, config.ALTURA_TELA))
        self.img_borda_dir = self.carregar_imagem("borda_direita.png", (config.TAMANHO_BLOCO, config.ALTURA_TELA))
        self.imagem_fundo_menu = self.carregar_imagem("TetrizosFundo.png", (config.LARGURA_TELA, config.ALTURA_TELA))
        self.imagem_pause = self.carregar_imagem("layout_pause.png", (400, 300))
        
        self.em_animacao_limpeza_linha = False; self.tempo_inicio_animacao = 0; self.linhas_a_limpar = []
        self.peca_atual = None; self.proximas_pecas = []; self.peca_segurada = None; self.pode_segurar = True
        self.peca_fantasma = None; self.score = 0; self.linhas_limpas = 0; self.nivel = 1
        self.ultimo_tempo_queda = time.time(); self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[0]
        self.fim_de_jogo = False; self.pausado = False; self.estado_jogo = "menu"
        self.tempo_inicio_jogo = 0; self.duracao_jogo = 0; self.tempo_peca_no_chao = 0; self.peca_tocando_chao = False
        self.tempo_inicio_fim_de_jogo = 0; self.id_ultimo_score = None; self.nickname = ""
        y_base_menu = config.ALTURA_TELA // 2 + 80
        self.botoes_menu_principal = {"iniciar": pygame.Rect(config.LARGURA_TELA // 2 - 100, y_base_menu, 200, 50), "sair": pygame.Rect(config.LARGURA_TELA // 2 - 100, y_base_menu + 70, 200, 50)}
        self.nickname_box = TextInputBox(config.LARGURA_TELA // 2 - 150, y_base_menu - 70, 300, 50, self.font_secundaria)
        self.nomes_botoes_fim_de_jogo = ["Menu Principal", "Reiniciar"]; self.botoes_fim_de_jogo_rects = {}
        self.move_esquerda_pressionado = False; self.move_direita_pressionado = False; self.queda_suave_pressionado = False
        self.tempo_inicial_das = 0; self.ultimo_tempo_arr = 0
        database.inicializar_banco_dados()

    def carregar_imagem(self, nome_arquivo, tamanho):
        caminho = os.path.join("recursos", nome_arquivo)
        try:
            img = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except pygame.error as e:
            print(f"AVISO: Não foi possivel carregar a imagem '{caminho}': {e}")
            return None

    def criar_grid_vazio(self):
        return [[0 for _ in range(config.GRID_COLUNAS)] for _ in range(config.GRID_LINHAS_TOTAL)]

    def desenhar_painel_customizado(self, tela, rect, cor_borda, texto_titulo=""):
        sombra_rect = rect.copy(); sombra_rect.move_ip(4, 4)
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, config.COR_PAINEL_SOMBRA, s.get_rect(), border_radius=8)
        tela.blit(s, sombra_rect)
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, config.COR_PAINEL_FUNDO_NEON, s.get_rect(), border_radius=8)
        tela.blit(s, rect)
        pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=8)
        if texto_titulo:
            titulo_surface = self.font_secundaria.render(texto_titulo, True, config.BRANCO)
            tela.blit(titulo_surface, (rect.x + 20, rect.y + 15))

    def atualizar(self):
        if self.fim_de_jogo or self.pausado or self.estado_jogo != "jogando": return
        if self.em_animacao_limpeza_linha: self.processar_limpeza_linha(); return
        if not self.peca_atual:
            self.gerar_nova_peca()
            if self.fim_de_jogo: return
        
        tempo_atual = time.time(); tempo_ms = tempo_atual * 1000
        if self.move_esquerda_pressionado and tempo_ms - self.tempo_inicial_das > config.ATRASO_DAS:
            if tempo_ms - self.ultimo_tempo_arr > config.TAXA_ARR: self.mover_peca(-1, 0); self.ultimo_tempo_arr = tempo_ms
        elif self.move_direita_pressionado and tempo_ms - self.tempo_inicial_das > config.ATRASO_DAS:
            if tempo_ms - self.ultimo_tempo_arr > config.TAXA_ARR: self.mover_peca(1, 0); self.ultimo_tempo_arr = tempo_ms
        pode_mover_para_baixo = self.e_espaco_valido(self.peca_atual, deslocamento_y=1)
        if not pode_mover_para_baixo:
            if not self.peca_tocando_chao: self.peca_tocando_chao = True; self.tempo_peca_no_chao = tempo_atual
            if tempo_atual - self.tempo_peca_no_chao > config.TEMPO_FIXAR_PECA: self.fixar_peca()
        else: self.peca_tocando_chao = False
        intervalo_de_queda = 0.05 if self.queda_suave_pressionado else self.intervalo_queda
        if tempo_atual - self.ultimo_tempo_queda > intervalo_de_queda:
            if self.mover_peca(0, 1) and self.queda_suave_pressionado: self.score += 1
            self.ultimo_tempo_queda = tempo_atual

    def fixar_peca(self):
        if not self.peca_atual: return
        coords = self.peca_atual.obter_coords_forma()
        for x, y in coords:
            if 0 <= x < config.GRID_COLUNAS and 0 <= y < config.GRID_LINHAS_TOTAL: self.grid[y][x] = self.peca_atual.cor
            else: self.finalizar_jogo(); return
        self.peca_atual = None
        if not self.verificar_e_iniciar_limpeza_de_linha():
            self.pode_segurar = True
            if not self.fim_de_jogo: self.gerar_nova_peca()

    def verificar_e_iniciar_limpeza_de_linha(self):
        self.linhas_a_limpar = [r for r, linha in enumerate(self.grid) if all(bloco != 0 for bloco in linha)]
        if self.linhas_a_limpar:
            self.em_animacao_limpeza_linha = True; self.tempo_inicio_animacao = time.time()
            self.atualizar_nivel_e_score(len(self.linhas_a_limpar)); return True
        return False

    def processar_limpeza_linha(self):
        if time.time() - self.tempo_inicio_animacao > config.DURACAO_ANIMACAO_LINHA:
            for r in sorted(self.linhas_a_limpar, reverse=True):
                self.grid.pop(r); self.grid.insert(0, [0 for _ in range(config.GRID_COLUNAS)])
            self.em_animacao_limpeza_linha = False; self.linhas_a_limpar = []
            self.pode_segurar = True
            if not self.fim_de_jogo: self.gerar_nova_peca()

    def desenhar(self):
        self.tela.fill(config.COR_FUNDO)
        if self.estado_jogo == "menu": self.desenhar_menu_principal()
        elif self.estado_jogo == "fim_de_jogo": self.desenhar_tela_fim_de_jogo()
        else:
            self.desenhar_grid()
            self.desenhar_peca(self.peca_fantasma, e_fantasma=True)
            self.desenhar_peca(self.peca_atual)
            self.desenhar_proximas_pecas()
            self.desenhar_peca_segurada()
            self.desenhar_informacoes_jogo()
            self.desenhar_info_pausa()
            if self.em_animacao_limpeza_linha: self.desenhar_linhas_piscando()
            if self.pausado: self.desenhar_tela_pausado()
        pygame.display.flip()
    
    def desenhar_painel(self, x, y, largura, altura, titulo):
        painel_rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(self.tela, config.COR_PAINEL_FUNDO, painel_rect, border_radius=5)
        pygame.draw.rect(self.tela, config.COR_PAINEL_BORDA, painel_rect, 2, border_radius=5)
        texto_titulo = self.font_placar.render(titulo, True, config.COR_TEXTO)
        self.tela.blit(texto_titulo, (painel_rect.x + 15, painel_rect.y + 10))

    def desenhar_proximas_pecas(self):
        y_pos, altura_painel = config.CANTO_SUPERIOR_Y, 240
        self.desenhar_painel(config.PAINEL_INFO_X, y_pos, config.PAINEL_INFO_LARGURA, altura_painel, "PRÓXIMAS")
        if self.proximas_pecas:
            self.desenhar_peca_em_caixa(self.proximas_pecas[0], config.PAINEL_INFO_X, y_pos + 40, pulsar=True)
            if len(self.proximas_pecas) > 1: self.desenhar_peca_em_caixa(self.proximas_pecas[1], config.PAINEL_INFO_X, y_pos + 130)

    def desenhar_peca_segurada(self):
        y_pos, altura_painel = config.CANTO_SUPERIOR_Y + 260, 150
        self.desenhar_painel(config.PAINEL_INFO_X, y_pos, config.PAINEL_INFO_LARGURA, altura_painel, "GUARDADA")
        tecla_rect = pygame.Rect(config.PAINEL_INFO_X + 15, y_pos + altura_painel - 45, 30, 30)
        pygame.draw.rect(self.tela, config.COR_TECLA_HOLD, tecla_rect, border_radius=4)
        pygame.draw.rect(self.tela, config.COR_PAINEL_BORDA, tecla_rect, 1, border_radius=4)
        texto_c = self.font_placar.render("C", True, config.COR_TEXTO)
        self.tela.blit(texto_c, texto_c.get_rect(center=tecla_rect.center))
        if self.peca_segurada: self.desenhar_peca_em_caixa(self.peca_segurada, config.PAINEL_INFO_X, y_pos + 40)
            
    def desenhar_informacoes_jogo(self):
        y_pos, altura_painel = config.CANTO_SUPERIOR_Y + 430, 160
        self.desenhar_painel(config.PAINEL_INFO_X, y_pos, config.PAINEL_INFO_LARGURA, altura_painel, "PLACAR")
        info = {"PONTOS": self.score, "NÍVEL": self.nivel, "LINHAS": self.linhas_limpas}
        y_offset = y_pos + 50
        for chave, valor in info.items():
            texto_chave = self.font_placar.render(chave, True, config.COR_TEXTO)
            self.tela.blit(texto_chave, (config.PAINEL_INFO_X + 20, y_offset))
            texto_valor = self.font_secundaria.render(str(valor), True, config.BRANCO)
            pos_valor = texto_valor.get_rect(right=config.PAINEL_INFO_X + config.PAINEL_INFO_LARGURA - 20, centery=texto_chave.get_rect(centery=y_offset).centery)
            self.tela.blit(texto_valor, pos_valor)
            y_offset += 40

    def desenhar_peca(self, peca, e_fantasma=False):
        if not peca: return
        coords = peca.obter_coords_forma()
        for x, y in coords:
            if y >= config.GRID_LINHAS_INVISIVEIS:
                y_desenho = (y - config.GRID_LINHAS_INVISIVEIS) * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_Y
                x_desenho = x * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_X
                if e_fantasma:
                    s = pygame.Surface((config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), pygame.SRCALPHA)
                    s.fill((*config.COR_BASE_FANTASMA, config.ALPHA_COR_FANTASMA))
                    self.tela.blit(s, (x_desenho, y_desenho))
                else:
                    pygame.draw.rect(self.tela, peca.cor, (x_desenho, y_desenho, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO))
                    pygame.draw.rect(self.tela, config.PRETO, (x_desenho, y_desenho, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), 1)

    def desenhar_linhas_piscando(self):
        if int((time.time() - self.tempo_inicio_animacao) * 1000 / config.INTERVALO_PISCAR_LINHA) % 2 == 0:
            for r in self.linhas_a_limpar:
                if r >= config.GRID_LINHAS_INVISIVEIS:
                    y_desenho = (r - config.GRID_LINHAS_INVISIVEIS) * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_Y
                    rect_linha = pygame.Rect(config.CANTO_SUPERIOR_X, y_desenho, config.LARGURA_JOGO, config.TAMANHO_BLOCO)
                    pygame.draw.rect(self.tela, config.BRANCO, rect_linha)
    
    def hard_drop(self):
        if self.fim_de_jogo or not self.peca_atual: return
        if self.peca_fantasma:
            y_inicial = self.peca_atual.y; self.peca_atual.y = self.peca_fantasma.y
            distancia = self.peca_atual.y - y_inicial
            self.score += distancia * 2; self.fixar_peca()

    def atualizar_nivel_e_score(self, num_linhas_limpas):
        if num_linhas_limpas > 0:
            self.linhas_limpas += num_linhas_limpas; pontos = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += pontos.get(num_linhas_limpas, 0) * self.nivel
            novo_nivel = (self.linhas_limpas // 10) + 1
            if novo_nivel > self.nivel:
                self.nivel = min(novo_nivel, len(config.VELOCIDADES_QUEDA_NIVEL))
                self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[self.nivel - 1]

    def desenhar_peca_em_caixa(self, peca, box_x, box_y, pulsar=False):
        if not peca: return
        forma, cor = peca.forma[0], peca.cor
        min_x = min(c[0] for c in forma); min_y = min(c[1] for c in forma)
        tamanho_bloco_final = config.TAMANHO_BLOCO
        if pulsar:
            escala = 1.0 + 0.1 * math.sin(time.time() * 5); tamanho_bloco_final = int(config.TAMANHO_BLOCO * escala)
        largura_peca = (max(c[0] for c in forma) - min_x + 1) * tamanho_bloco_final
        altura_peca = (max(c[1] for c in forma) - min_y + 1) * tamanho_bloco_final
        offset_x = box_x + (config.PAINEL_INFO_LARGURA - largura_peca) / 2
        offset_y = box_y + (100 - altura_peca) / 2
        for dx, dy in forma:
            px = offset_x + (dx - min_x) * tamanho_bloco_final; py = offset_y + (dy - min_y) * tamanho_bloco_final
            pygame.draw.rect(self.tela, cor, (px, py, tamanho_bloco_final, tamanho_bloco_final))
            pygame.draw.rect(self.tela, config.PRETO, (px, py, tamanho_bloco_final, tamanho_bloco_final), 1)

    def desenhar_tela_pausado(self):
        s = pygame.Surface((config.LARGURA_TELA, config.ALTURA_TELA), pygame.SRCALPHA); s.fill(config.COR_OVERLAY_PAUSA); self.tela.blit(s, (0, 0))
        if self.imagem_pause:
            rect_pause = self.imagem_pause.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2))
            self.tela.blit(self.imagem_pause, rect_pause)
        else:
            texto_pausado = self.font_principal.render("PAUSADO", True, config.BRANCO)
            self.tela.blit(texto_pausado, texto_pausado.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2)))

    def atualizar_peca_fantasma(self):
        if not self.peca_atual: self.peca_fantasma = None; return
        peca_fantasma_teste = Peca(self.peca_atual.x, self.peca_atual.y, self.peca_atual.nome_forma)
        peca_fantasma_teste.rotacao = self.peca_atual.rotacao
        while self.e_espaco_valido(peca_fantasma_teste, deslocamento_y=1): peca_fantasma_teste.mover(0, 1)
        self.peca_fantasma = peca_fantasma_teste

    def gerar_nova_peca(self):
        if self.fim_de_jogo: return
        nomes_formas = list(config.TETROMINOS.keys())
        while len(self.proximas_pecas) < 4:
            nome_forma = random.choice(nomes_formas)
            self.proximas_pecas.append(Peca(config.GRID_COLUNAS // 2 - 2, 0, nome_forma))
        self.peca_atual = self.proximas_pecas.pop(0)
        if not self.e_espaco_valido(self.peca_atual): self.finalizar_jogo()
        else: self.atualizar_peca_fantasma()

    def e_espaco_valido(self, peca_teste, deslocamento_x=0, deslocamento_y=0, verificar_rotacao=None):
        coords = peca_teste.obter_coords_forma(rotacao=verificar_rotacao)
        for x, y in coords:
            xf, yf = int(x + deslocamento_x), int(y + deslocamento_y)
            if not (0 <= xf < config.GRID_COLUNAS and yf < config.GRID_LINHAS_TOTAL): return False
            if 0 <= yf and self.grid[yf][xf] != 0: return False
        return True

    def mover_peca(self, dx, dy):
        if self.fim_de_jogo or not self.peca_atual: return False
        if self.e_espaco_valido(self.peca_atual, dx, dy):
            self.peca_atual.mover(dx, dy); self.atualizar_peca_fantasma()
            if self.peca_tocando_chao: self.tempo_peca_no_chao = time.time()
            return True
        return False

    def lidar_com_rotacao(self, sentido_horario=True):
        if self.fim_de_jogo or not self.peca_atual: return
        peca = self.peca_atual
        if len(peca.forma) == 1: return
        rotacao_original = peca.rotacao; num_rotacoes = len(peca.forma)
        rotacao_alvo = (rotacao_original + 1) % num_rotacoes if sentido_horario else (rotacao_original - 1 + num_rotacoes) % num_rotacoes
        testes_deslocamento = [(0, 0)]; tabela = config.DESLOCAMENTOS_I if peca.nome_forma == 'I' else config.DESLOCAMENTOS_JLSTZ
        chave = (rotacao_original, rotacao_alvo)
        if chave in tabela:
            for dx_srs, dy_srs in tabela[chave]: testes_deslocamento.append((dx_srs, -dy_srs))
        for dx, dy in testes_deslocamento:
            if self.e_espaco_valido(peca, dx, dy, verificar_rotacao=rotacao_alvo):
                peca.x += dx; peca.y += dy; peca.rotacao = rotacao_alvo
                self.atualizar_peca_fantasma()
                if self.peca_tocando_chao: self.tempo_peca_no_chao = time.time()
                return

    def segurar_peca(self):
        if self.fim_de_jogo or not self.pode_segurar: return
        self.pode_segurar = False; peca_temporaria = self.peca_atual
        if self.peca_segurada is None:
            self.peca_segurada = peca_temporaria; self.gerar_nova_peca()
        else:
            self.peca_atual = self.peca_segurada; self.peca_segurada = peca_temporaria
        self.peca_segurada.rotacao = 0 
        self.peca_atual.x = config.GRID_COLUNAS // 2 - 1; self.peca_atual.y = 0
        if not self.e_espaco_valido(self.peca_atual): self.finalizar_jogo()
        else: self.atualizar_peca_fantasma()

    def desenhar_grid(self):
        self.tela.fill(config.COR_FUNDO)
        
        fundo_grid_rect = pygame.Rect(config.CANTO_SUPERIOR_X, config.CANTO_SUPERIOR_Y, config.LARGURA_JOGO, config.ALTURA_JOGO)
        pygame.draw.rect(self.tela, config.PRETO, fundo_grid_rect)
        
        for x in range(config.CANTO_SUPERIOR_X, config.CANTO_SUPERIOR_X + config.LARGURA_JOGO + 1, config.TAMANHO_BLOCO):
            pygame.draw.line(self.tela, config.COR_GRID, (x, config.CANTO_SUPERIOR_Y), (x, config.CANTO_SUPERIOR_Y + config.ALTURA_JOGO))
        for y in range(config.CANTO_SUPERIOR_Y, config.CANTO_SUPERIOR_Y + config.ALTURA_JOGO + 1, config.TAMANHO_BLOCO):
            pygame.draw.line(self.tela, config.COR_GRID, (config.CANTO_SUPERIOR_X, y), (config.CANTO_SUPERIOR_X + config.LARGURA_JOGO, y))

        for r, row in enumerate(self.grid):
            if r < config.GRID_LINHAS_INVISIVEIS: continue
            for c, cor in enumerate(row):
                if cor != 0:
                    y_pos = (r - config.GRID_LINHAS_INVISIVEIS) * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_Y
                    x_pos = c * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_X
                    pygame.draw.rect(self.tela, cor, (x_pos, y_pos, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO))
                    pygame.draw.rect(self.tela, config.PRETO, (x_pos, y_pos, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), 1)
        
        pygame.draw.rect(self.tela, config.BRANCO, fundo_grid_rect, 3)

    def reiniciar_jogo(self):
        if not self.nickname_box.text.strip(): return
        self.nickname = self.nickname_box.text; self.grid = self.criar_grid_vazio(); self.proximas_pecas.clear()
        self.peca_segurada = None; self.pode_segurar = True; self.score, self.linhas_limpas, self.nivel = 0, 0, 1
        self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[0]
        self.ultimo_tempo_queda = self.tempo_inicio_jogo = time.time()
        self.fim_de_jogo, self.pausado = False, False; self.gerar_nova_peca()
        self.estado_jogo = "jogando"

    def desenhar_info_pausa(self):
        texto = self.font_placar.render("Pressione ESPAÇO para pausar", True, config.CINZA)
        self.tela.blit(texto, texto.get_rect(centerx=config.LARGURA_TELA // 2, bottom=config.ALTURA_TELA - 20))

    def desenhar_menu_principal(self):
        if self.imagem_fundo_menu: self.tela.blit(self.imagem_fundo_menu, (0, 0))
        else: self.tela.fill(config.COR_FUNDO)
        mouse_pos = pygame.mouse.get_pos()
        for nome, rect in self.botoes_menu_principal.items():
            cor = config.COR_BOTAO_MENU_HOVER if rect.collidepoint(mouse_pos) else config.COR_BOTAO_MENU
            pygame.draw.rect(self.tela, cor, rect, 0, 5)
            pygame.draw.rect(self.tela, config.BRANCO, rect, 2, 5)
            texto = self.font_secundaria.render(nome.title(), True, config.COR_TEXTO_MENU)
            self.tela.blit(texto, texto.get_rect(center=rect.center))
        self.nickname_box.draw(self.tela)

    def desenhar_tela_fim_de_jogo(self):
        self.tela.fill(config.COR_FUNDO)
        
        if self.img_borda_esq:
            self.tela.blit(self.img_borda_esq, (0, 0))
        if self.img_borda_dir:
            self.tela.blit(self.img_borda_dir, (config.LARGURA_TELA - config.TAMANHO_BLOCO, 0))
        
        game_surf = self.font_pixel.render("GAME", True, config.COR_TITULO_GAME)
        over_surf = self.font_pixel.render("OVER", True, config.COR_TITULO_OVER)
        game_rect = game_surf.get_rect(center=(config.LARGURA_TELA / 2, 80))
        over_rect = over_surf.get_rect(center=(config.LARGURA_TELA / 2, 160))
        self.tela.blit(game_surf, game_rect); self.tela.blit(over_surf, over_rect)
        
        stats_rect = pygame.Rect(0, 0, 450, 140)
        stats_rect.center = (config.LARGURA_TELA / 2, 280)
        self.desenhar_painel_customizado(self.tela, stats_rect, config.COR_PAINEL_BORDA_NEON, "SUA PONTUAÇÃO")
        
        stats = {"Jogador": self.nickname, "Pontos": self.score, "Tempo": time.strftime("%M:%S", time.gmtime(self.duracao_jogo))}
        y_offset = stats_rect.y + 55
        for chave, valor in stats.items():
            texto_chave = self.font_placar.render(f"{chave}:", True, config.CINZA)
            self.tela.blit(texto_chave, (stats_rect.x + 30, y_offset))
            texto_valor = self.font_secundaria.render(str(valor), True, config.BRANCO)
            self.tela.blit(texto_valor, texto_valor.get_rect(right=stats_rect.right - 30, centery=texto_chave.get_rect(centery=y_offset).centery))
            y_offset += 35
            
        ranking_rect = pygame.Rect(0, 0, 450, 220)
        ranking_rect.center = (config.LARGURA_TELA / 2, 475)
        self.desenhar_painel_customizado(self.tela, ranking_rect, config.COR_PAINEL_BORDA_NEON, "RANKING GERAL")
        
        scores = database.carregar_ultimos_scores_db(5)
        y_inicial_ranking = ranking_rect.y + 60
        y_offset_ranking = 30
        for i, (score_id, nick, pont) in enumerate(scores):
            y_atual = y_inicial_ranking + (i * y_offset_ranking)
            is_player_score = (score_id == self.id_ultimo_score)
            cor_pos = config.OURO if i == 0 else config.PRATA if i == 1 else config.BRONZE if i == 2 else config.CINZA
            pos_surf = self.font_placar.render(f"{i + 1}º", True, cor_pos)
            self.tela.blit(pos_surf, (ranking_rect.x + 30, y_atual))
            nick_surf = self.font_placar.render(nick, True, config.BRANCO)
            self.tela.blit(nick_surf, (ranking_rect.x + 90, y_atual))
            pont_surf = self.font_placar.render(f"{pont} pts", True, config.BRANCO)
            self.tela.blit(pont_surf, pont_surf.get_rect(right=ranking_rect.right - 30, centery=pos_surf.get_rect(centery=y_atual).centery))
            if is_player_score:
                underline_rect = pygame.Rect(ranking_rect.x + 20, y_atual + 25, ranking_rect.w - 40, 2)
                pygame.draw.rect(self.tela, config.COR_DESTAQUE_JOGADOR, underline_rect)
                
        mouse_pos = pygame.mouse.get_pos()
        y_botoes = ranking_rect.bottom + 20
        self.botoes_fim_de_jogo_rects.clear()
        for nome_botao in self.nomes_botoes_fim_de_jogo:
            rect_botao = pygame.Rect(0, 0, 300, 50)
            rect_botao.center = (config.LARGURA_TELA / 2, y_botoes)
            self.botoes_fim_de_jogo_rects[nome_botao] = rect_botao
            cor_borda = config.COR_BOTAO_NEON_HOVER if rect_botao.collidepoint(mouse_pos) else config.COR_PAINEL_BORDA_NEON
            self.desenhar_painel_customizado(self.tela, rect_botao, cor_borda)
            texto = self.font_secundaria.render(nome_botao, True, config.BRANCO)
            self.tela.blit(texto, texto.get_rect(center=rect_botao.center))
            y_botoes += 60

    def finalizar_jogo(self):
        if self.fim_de_jogo: return
        self.fim_de_jogo = True
        self.duracao_jogo = time.time() - self.tempo_inicio_jogo
        self.id_ultimo_score = database.salvar_score_db(self.nickname, self.score, int(self.duracao_jogo))
        self.estado_jogo = "fim_de_jogo"
        self.tempo_inicio_fim_de_jogo = time.time()