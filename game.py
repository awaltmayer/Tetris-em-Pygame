import pygame
import random
import time
import os
import sys # Importa a biblioteca 'sys'
import math
import speech_recognition as sr
import pyttsx3
import threading

import config
from player import Peca
import database
from widgets import TextInputBox
import utils
import logger

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ObjetoDecorativo:
    # ... (o resto da classe ObjetoDecorativo não muda)
    def __init__(self):
        self.x = random.randint(0, config.LARGURA_TELA)
        self.y = random.randint(0, config.ALTURA_TELA)
        self.tamanho = random.randint(1, 4)
        self.velocidade_x = random.uniform(-0.5, 0.5)
        self.velocidade_y = random.uniform(-0.5, 0.5)
        self.cor = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def atualizar(self):
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        if self.x < 0 or self.x > config.LARGURA_TELA:
            self.velocidade_x *= -1
        if self.y < 0 or self.y > config.ALTURA_TELA:
            self.velocidade_y *= -1

    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (self.x, self.y), self.tamanho)


class Tetris:
    def __init__(self, tela):
        self.tela = tela
        self.grid = self.criar_grid_vazio()
        self.rodando = True

        self._carregar_fontes()
        self._carregar_imagens()
        
        self.objetos_decorativos = [ObjetoDecorativo() for _ in range(150)]
        
        # ... (o resto do __init__ não muda) ...
        self.em_animacao_limpeza_linha = False; self.tempo_inicio_animacao = 0; self.linhas_a_limpar = []
        self.peca_atual = None; self.proximas_pecas = []; self.peca_segurada = None; self.pode_segurar = True
        self.peca_fantasma = None; self.score = 0; self.linhas_limpas = 0; self.nivel = 1
        self.ultimo_tempo_queda = time.time(); self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[0]
        self.fim_de_jogo = False; self.pausado = False; self.estado_jogo = "menu"
        self.tempo_inicio_jogo = 0; self.duracao_jogo = 0; self.tempo_peca_no_chao = 0; self.peca_tocando_chao = False
        self.id_ultimo_score = None; self.nickname = ""

        y_base_menu = config.ALTURA_TELA // 2 + 80
        self.botoes_menu_principal = {"iniciar": pygame.Rect(config.LARGURA_TELA // 2 - 100, y_base_menu, 200, 50), "sair": pygame.Rect(config.LARGURA_TELA // 2 - 100, y_base_menu + 70, 200, 50)}
        self.nickname_box = TextInputBox(config.LARGURA_TELA // 2 - 150, y_base_menu - 70, 300, 50, self.font_secundaria)
        self.botao_iniciar_welcome = pygame.Rect(config.LARGURA_TELA // 2 - 125, config.ALTURA_TELA - 120, 250, 60)
        
        self.move_esquerda_pressionado = False; self.move_direita_pressionado = False; self.queda_suave_pressionado = False
        self.tempo_inicial_das = 0; self.ultimo_tempo_arr = 0
        
        database.inicializar_banco_dados()
        self._inicializar_voz()
        
    def _carregar_fontes(self):
        # --- ALTERAÇÃO: Usa a nova função resource_path ---
        try:
            self.font_principal = pygame.font.Font(resource_path("recursos/font.ttf"), 36)
            self.font_secundaria = pygame.font.Font(resource_path("recursos/font.ttf"), 28)
            self.font_placar = pygame.font.Font(resource_path("recursos/font.ttf"), 22)
            self.font_placar_grande = pygame.font.Font(resource_path("recursos/font.ttf"), 48)
            self.font_welcome = pygame.font.Font(resource_path("recursos/font.ttf"), 24)
            self.font_welcome_instrucoes = pygame.font.Font(resource_path("recursos/font.ttf"), 18)
        except FileNotFoundError:
            self.font_principal = pygame.font.Font(None, 42)
            self.font_secundaria = pygame.font.Font(None, 34)
            self.font_placar = pygame.font.Font(None, 28)
            self.font_placar_grande = pygame.font.Font(None, 54)
            self.font_welcome = pygame.font.Font(None, 30)
            self.font_welcome_instrucoes = pygame.font.Font(None, 24)

    def _carregar_imagens(self):

        self.imagem_fundo_menu = self.carregar_imagem(resource_path("recursos/TetrizosFundo.png"), (config.LARGURA_TELA, config.ALTURA_TELA))
        self.imagem_fundo_game_over = self.carregar_imagem(resource_path("recursos/fundoGame.png"), (config.LARGURA_TELA, config.ALTURA_TELA))
        self.imagem_pause = self.carregar_imagem(resource_path("recursos/layout_pause.png"), (400, 300))

    def _inicializar_voz(self):
        self.comando_de_voz = None
        try:
            self.tts_engine = pyttsx3.init()
            self.reconhecedor = sr.Recognizer()
            
            thread_voz = threading.Thread(target=self.ouvir_comandos_em_background)
            thread_voz.daemon = True
            thread_voz.start()
        except Exception as e:
            print(f"Não foi possível inicializar os recursos de voz: {e}")
            self.tts_engine = None
            self.reconhecedor = None

    def falar(self, texto):
        if not self.tts_engine: return
        try:
            self.tts_engine.say(texto)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Erro no motor de TTS: {e}")

    def ouvir_comandos_em_background(self):
        if not self.reconhecedor: return
        with sr.Microphone() as source:
            self.reconhecedor.adjust_for_ambient_noise(source, duration=0.5)
            while self.rodando:
                try:
                    audio = self.reconhecedor.listen(source, timeout=5, phrase_time_limit=3)
                    texto = self.reconhecedor.recognize_google(audio, language='pt-BR').lower()
                    print(f"Comando de voz reconhecido: {texto}")
                    if "iniciar" in texto:
                        self.comando_de_voz = "iniciar"
                    elif "sair" in texto:
                        self.comando_de_voz = "sair"
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    pass
                except Exception as e:
                    print(f"Erro no reconhecimento de voz: {e}")
                    time.sleep(1)

    def carregar_imagem(self, caminho_completo, tamanho):
        # --- ALTERAÇÃO: Recebe o caminho completo da nova função ---
        try:
            img = pygame.image.load(caminho_completo).convert_alpha()
            return pygame.transform.scale(img, tamanho)
        except pygame.error:
            return None

    def criar_grid_vazio(self):
        return [[0 for _ in range(config.GRID_COLUNAS)] for _ in range(config.GRID_LINHAS_TOTAL)]

    def atualizar(self):
        if self.comando_de_voz:
            if self.estado_jogo == "menu":
                if self.comando_de_voz == "iniciar" and self.nickname_box.text.strip():
                    self.ir_para_welcome()
                elif self.comando_de_voz == "sair":
                    self.rodando = False
            self.comando_de_voz = None

        if self.estado_jogo != 'fim_de_jogo':
            for obj in self.objetos_decorativos:
                obj.atualizar()
        
        if self.fim_de_jogo or self.pausado or self.estado_jogo != "jogando":
            return
        if self.em_animacao_limpeza_linha:
            self.processar_limpeza_linha(); return
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
            if not self.peca_tocando_chao:
                self.peca_tocando_chao = True; self.tempo_peca_no_chao = tempo_atual
            if tempo_atual - self.tempo_peca_no_chao > config.TEMPO_FIXAR_PECA:
                self.fixar_peca()
        else:
            self.peca_tocando_chao = False
        
        intervalo_de_queda = 0.05 if self.queda_suave_pressionado else self.intervalo_queda
        if tempo_atual - self.ultimo_tempo_queda > intervalo_de_queda:
            if self.mover_peca(0, 1) and self.queda_suave_pressionado:
                self.score += 1
            self.ultimo_tempo_queda = tempo_atual

    def fixar_peca(self):
        if not self.peca_atual: return
        coords = self.peca_atual.obter_coords_forma()
        for x, y in coords:
            if 0 <= x < config.GRID_COLUNAS and 0 <= y < config.GRID_LINHAS_TOTAL:
                self.grid[y][x] = self.peca_atual.cor
            else:
                self.finalizar_jogo(); return
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
        if self.estado_jogo == "menu":
            if self.imagem_fundo_menu: self.tela.blit(self.imagem_fundo_menu, (0,0))
            else: self.tela.fill(config.COR_FUNDO)
        elif self.estado_jogo == "fim_de_jogo":
            if self.imagem_fundo_game_over: self.tela.blit(self.imagem_fundo_game_over, (0, 0))
            else: self.tela.fill(config.COR_FUNDO)
        else:
            self.tela.fill(config.PRETO)

        if self.estado_jogo in ["welcome", "jogando"]:
            for obj in self.objetos_decorativos:
                obj.desenhar(self.tela)
        
        if self.estado_jogo == "jogando":
            self.desenhar_grid()
            self.desenhar_peca(self.peca_fantasma, e_fantasma=True)
            self.desenhar_peca(self.peca_atual)
            self.desenhar_proximas_pecas()
            self.desenhar_peca_segurada()
            self.desenhar_informacoes_jogo()
            self.desenhar_info_pausa()
            if self.em_animacao_limpeza_linha: self.desenhar_linhas_piscando()
            if self.pausado: self.desenhar_tela_pausado()
        elif self.estado_jogo == "menu":
            self.desenhar_menu_principal()
        elif self.estado_jogo == "welcome":
            self.desenhar_tela_welcome()
        elif self.estado_jogo == "fim_de_jogo":
            self.desenhar_tela_fim_de_jogo()
        
        pygame.display.flip()

    def desenhar_grid(self):
        fundo_grid_rect = pygame.Rect(config.CANTO_SUPERIOR_X, config.CANTO_SUPERIOR_Y, config.LARGURA_JOGO, config.ALTURA_JOGO)
        s = pygame.Surface((config.LARGURA_JOGO, config.ALTURA_JOGO), pygame.SRCALPHA)
        s.fill((20, 20, 30, 180))
        self.tela.blit(s, fundo_grid_rect.topleft)
        
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
                    cor_bloco = cor
                    cor_borda = (max(0, cor[0]-50), max(0, cor[1]-50), max(0, cor[2]-50))
                    pygame.draw.rect(self.tela, cor_bloco, (x_pos, y_pos, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO))
                    pygame.draw.rect(self.tela, cor_borda, (x_pos, y_pos, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), 2)
        
        pygame.draw.rect(self.tela, config.BRANCO, fundo_grid_rect, 2)

    def desenhar_peca(self, peca, e_fantasma=False):
        if not peca: return
        coords = peca.obter_coords_forma()
        for x, y in coords:
            if y >= config.GRID_LINHAS_INVISIVEIS:
                y_desenho = (y - config.GRID_LINHAS_INVISIVEIS) * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_Y
                x_desenho = x * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_X
                if e_fantasma:
                    s = pygame.Surface((config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), pygame.SRCALPHA)
                    pygame.draw.rect(s, (*peca.cor, 50), s.get_rect(), border_radius=3)
                    pygame.draw.rect(s, (*config.BRANCO, 100), s.get_rect(), 1, border_radius=3)
                    self.tela.blit(s, (x_desenho, y_desenho))
                else:
                    cor_bloco = peca.cor
                    cor_borda = (max(0, cor_bloco[0]-50), max(0, cor_bloco[1]-50), max(0, cor_bloco[2]-50))
                    pygame.draw.rect(self.tela, cor_bloco, (x_desenho, y_desenho, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), border_radius=3)
                    pygame.draw.rect(self.tela, cor_borda, (x_desenho, y_desenho, config.TAMANHO_BLOCO, config.TAMANHO_BLOCO), 2, border_radius=3)

    def desenhar_linhas_piscando(self):
        if int((time.time() - self.tempo_inicio_animacao) * 1000 / config.INTERVALO_PISCAR_LINHA) % 2 == 0:
            for r in self.linhas_a_limpar:
                if r >= config.GRID_LINHAS_INVISIVEIS:
                    y_desenho = (r - config.GRID_LINHAS_INVISIVEIS) * config.TAMANHO_BLOCO + config.CANTO_SUPERIOR_Y
                    rect_linha = pygame.Rect(config.CANTO_SUPERIOR_X, y_desenho, config.LARGURA_JOGO, config.TAMANHO_BLOCO)
                    pygame.draw.rect(self.tela, config.BRANCO, rect_linha)
    
    def desenhar_proximas_pecas(self):
        rect = pygame.Rect(config.PAINEL_INFO_X, config.CANTO_SUPERIOR_Y, config.PAINEL_INFO_LARGURA, 240)
        pygame.draw.rect(self.tela, config.COR_PAINEL_FUNDO, rect, border_radius=5)
        if self.proximas_pecas:
            escala1 = 1.0 + 0.1 * abs(math.sin(time.time() * 5))
            self.desenhar_peca_em_caixa(self.proximas_pecas[0], rect.x, rect.y + 40, escala=escala1)
            
            if len(self.proximas_pecas) > 1:
                escala2 = 1.0 + 0.1 * abs(math.cos(time.time() * 5))
                self.desenhar_peca_em_caixa(self.proximas_pecas[1], rect.x, rect.y + 130, escala=escala2)

    def desenhar_peca_segurada(self):
        rect = pygame.Rect(config.PAINEL_INFO_X, config.CANTO_SUPERIOR_Y + 260, config.PAINEL_INFO_LARGURA, 150)
        pygame.draw.rect(self.tela, config.COR_PAINEL_FUNDO, rect, border_radius=5)
        if self.peca_segurada:
            self.desenhar_peca_em_caixa(self.peca_segurada, rect.x, rect.y + 40)

    def desenhar_peca_em_caixa(self, peca, box_x, box_y, escala=1.0):
        forma, cor = peca.forma[0], peca.cor
        min_x = min(c[0] for c in forma); min_y = min(c[1] for c in forma)
        tamanho_bloco = int(config.TAMANHO_BLOCO * escala)
        
        largura_peca = (max(c[0] for c in forma) - min_x + 1) * tamanho_bloco
        altura_peca = (max(c[1] for c in forma) - min_y + 1) * tamanho_bloco
        offset_x = box_x + (config.PAINEL_INFO_LARGURA - largura_peca) // 2
        offset_y = box_y + (100 - altura_peca) // 2
        for dx, dy in forma:
            px = offset_x + (dx - min_x) * tamanho_bloco
            py = offset_y + (dy - min_y) * tamanho_bloco
            cor_borda = (max(0, cor[0]-50), max(0, cor[1]-50), max(0, cor[2]-50))
            pygame.draw.rect(self.tela, cor, (px, py, tamanho_bloco, tamanho_bloco), border_radius=3)
            pygame.draw.rect(self.tela, cor_borda, (px, py, tamanho_bloco, tamanho_bloco), 2, border_radius=3)

    def desenhar_informacoes_jogo(self):
        rect = pygame.Rect(config.PAINEL_INFO_X, config.CANTO_SUPERIOR_Y + 430, config.PAINEL_INFO_LARGURA, 160)
        pygame.draw.rect(self.tela, config.COR_PAINEL_FUNDO, rect, border_radius=5)
        info = {"PONTOS": self.score, "NÍVEL": self.nivel, "LINHAS": self.linhas_limpas}
        y_offset = rect.y + 20
        for chave, valor in info.items():
            texto_chave = self.font_placar.render(chave, True, config.COR_TEXTO)
            self.tela.blit(texto_chave, (rect.x + 20, y_offset))
            texto_valor = self.font_secundaria.render(str(valor), True, config.BRANCO)
            self.tela.blit(texto_valor, texto_valor.get_rect(right=rect.right - 20, centery=texto_chave.get_rect(centery=y_offset).centery))
            y_offset += 40

    def desenhar_info_pausa(self):
        texto = self.font_placar.render("Pressione ESPAÇO para pausar", True, config.CINZA)
        self.tela.blit(texto, texto.get_rect(centerx=config.LARGURA_TELA // 2, bottom=config.ALTURA_TELA - 20))

    def desenhar_tela_pausado(self):
        overlay = pygame.Surface((config.LARGURA_TELA, config.ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        if self.imagem_pause:
            self.tela.blit(self.imagem_pause, self.imagem_pause.get_rect(center=(config.LARGURA_TELA/2, config.ALTURA_TELA/2)))
        else:
            texto_pausa = self.font_principal.render("PAUSADO", True, config.BRANCO)
            self.tela.blit(texto_pausa, texto_pausa.get_rect(center=(config.LARGURA_TELA/2, config.ALTURA_TELA/2)))

    def desenhar_menu_principal(self):
        mouse_pos = pygame.mouse.get_pos()
        for nome, rect in self.botoes_menu_principal.items():
            cor = config.COR_BOTAO_MENU_HOVER if rect.collidepoint(mouse_pos) else config.COR_BOTAO_MENU
            pygame.draw.rect(self.tela, cor, rect, border_radius=8)
            texto_surf = self.font_secundaria.render(nome.title(), True, config.BRANCO)
            self.tela.blit(texto_surf, texto_surf.get_rect(center=rect.center))
        self.nickname_box.draw(self.tela)
    
    def _desenhar_peca_exemplo(self, nome_peca, x, y):
        peca = Peca(0, 0, nome_peca)
        forma = peca.forma[0]
        cor = peca.cor
        tamanho_bloco = 15
        
        min_x = min(c[0] for c in forma); min_y = min(c[1] for c in forma)
        largura_peca = (max(c[0] for c in forma) - min_x + 1) * tamanho_bloco
        altura_peca = (max(c[1] for c in forma) - min_y + 1) * tamanho_bloco
        
        offset_x = x - largura_peca // 2
        offset_y = y - altura_peca // 2

        for dx, dy in forma:
            px = offset_x + (dx - min_x) * tamanho_bloco
            py = offset_y + (dy - min_y) * tamanho_bloco
            pygame.draw.rect(self.tela, cor, (px, py, tamanho_bloco, tamanho_bloco), border_radius=2)
            pygame.draw.rect(self.tela, config.PRETO, (px, py, tamanho_bloco, tamanho_bloco), 1, border_radius=2)

    def desenhar_tela_welcome(self):
        titulo = self.font_principal.render(f"Bem-vindo, {self.nickname}!", True, config.BRANCO)
        self.tela.blit(titulo, titulo.get_rect(centerx=config.LARGURA_TELA/2, y=50))
        
        objetivo_txt = self.font_welcome.render("O objetivo é completar linhas para marcar pontos. Não deixe as peças chegarem ao topo!", True, config.CINZA)
        self.tela.blit(objetivo_txt, objetivo_txt.get_rect(centerx=config.LARGURA_TELA/2, y=110))

        titulo_controles = self.font_secundaria.render("Como Jogar", True, config.BRANCO)
        self.tela.blit(titulo_controles, (150, 180))

        controles = {
            "Setas Esquerda/Direita": "Mover Peça",
            "Seta Cima": "Girar Peça",
            "Seta Baixo": "Acelerar Queda",
            "Enter": "Queda Rápida (Hard Drop)",
            "C": "Guardar Peça (Hold)",
            "Espaço": "Pausar o Jogo"
        }
        y_inst = 230
        for tecla, acao in controles.items():
            texto_tecla = self.font_welcome_instrucoes.render(f"{tecla}:", True, config.BRANCO)
            texto_acao = self.font_welcome_instrucoes.render(acao, True, config.CINZA)
            self.tela.blit(texto_tecla, (160, y_inst))
            self.tela.blit(texto_acao, (160 + texto_tecla.get_width() + 10, y_inst))
            y_inst += 35

        titulo_pecas = self.font_secundaria.render("As Peças", True, config.BRANCO)
        self.tela.blit(titulo_pecas, (650, 180))
        
        nomes_pecas = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        y_peca = 250
        for nome in nomes_pecas:
            self._desenhar_peca_exemplo(nome, 680, y_peca)
            nome_peca_surf = self.font_welcome_instrucoes.render(f"- Peça {nome}", True, config.CINZA)
            self.tela.blit(nome_peca_surf, (740, y_peca - 10))
            y_peca += 50
            
        mouse_pos = pygame.mouse.get_pos()
        cor_botao = config.COR_BOTAO_MENU_HOVER if self.botao_iniciar_welcome.collidepoint(mouse_pos) else config.COR_BOTAO_MENU
        pygame.draw.rect(self.tela, cor_botao, self.botao_iniciar_welcome, border_radius=8)
        texto_botao = self.font_secundaria.render("Iniciar Jogo", True, config.BRANCO)
        self.tela.blit(texto_botao, texto_botao.get_rect(center=self.botao_iniciar_welcome.center))

    def desenhar_tela_fim_de_jogo(self):
        nome_rect = config.RECT_GAMEOVER_NOME
        texto_nome_surf = self.font_placar_grande.render(self.nickname.upper(), True, config.BRANCO)
        area_texto = pygame.Rect(nome_rect.x + nome_rect.height, nome_rect.y, nome_rect.width - nome_rect.height, nome_rect.height)
        self.tela.blit(texto_nome_surf, texto_nome_surf.get_rect(center=area_texto.center))

        scores = database.carregar_ultimos_scores_db(5)
        for i, (score_id, nick, pont, duracao) in enumerate(scores):
            y_centro = config.RANKING_START_Y + (i * config.RANKING_LINE_HEIGHT)
            tempo_str = utils.formatar_tempo(duracao)
            cor = config.OURO if i == 0 else config.PRATA if i == 1 else config.BRONZE if i == 2 else config.BRANCO
            pos = self.font_secundaria.render(f"{i + 1}º", True, cor)
            self.tela.blit(pos, pos.get_rect(centerx=config.RANKING_COL_POS, centery=y_centro))
            nick_surf = self.font_secundaria.render(nick, True, config.BRANCO)
            self.tela.blit(nick_surf, nick_surf.get_rect(left=config.RANKING_COL_NICK, centery=y_centro))
            tempo_surf = self.font_secundaria.render(tempo_str, True, config.BRANCO)
            self.tela.blit(tempo_surf, tempo_surf.get_rect(centerx=config.RANKING_COL_TEMPO, centery=y_centro))
            pont_surf = self.font_secundaria.render(str(pont), True, config.BRANCO)
            self.tela.blit(pont_surf, pont_surf.get_rect(right=config.RANKING_COL_PONTOS, centery=y_centro))
        
        stats_rect = config.RECT_GAMEOVER_STATS
        titulo = self.font_secundaria.render("Minha Pontuação", True, config.BRANCO)
        self.tela.blit(titulo, titulo.get_rect(centerx=stats_rect.centerx, y=config.STATS_TITLE_Y))
        pontos_surf = self.font_placar_grande.render(str(self.score), True, config.BRANCO)
        self.tela.blit(pontos_surf, pontos_surf.get_rect(centerx=stats_rect.centerx, y=config.STATS_SCORE_Y))
        tempo_str = utils.formatar_tempo(self.duracao_jogo)
        tempo_surf = self.font_secundaria.render(tempo_str, True, config.BRANCO)
        self.tela.blit(tempo_surf, tempo_surf.get_rect(centerx=stats_rect.centerx, y=config.STATS_TIME_Y))

        mouse_pos = pygame.mouse.get_pos()
        botoes = {"Reiniciar": config.RECT_GAMEOVER_BOTAO_REINICIAR, "Menu Principal": config.RECT_GAMEOVER_BOTAO_MENU}
        for nome, rect in botoes.items():
            cor = config.COR_BOTAO_MENU_HOVER if rect.collidepoint(mouse_pos) else config.COR_BOTAO_MENU
            pygame.draw.rect(self.tela, cor, rect, border_radius=8)
            texto = self.font_secundaria.render(nome, True, config.BRANCO)
            self.tela.blit(texto, texto.get_rect(center=rect.center))

    def finalizar_jogo(self):
        if self.fim_de_jogo: return
        self.fim_de_jogo = True
        self.duracao_jogo = time.time() - self.tempo_inicio_jogo
        self.id_ultimo_score = database.salvar_score_db(self.nickname, self.score, int(self.duracao_jogo))
        logger.salvar_log(self.score)
        self.estado_jogo = "fim_de_jogo"
        if self.tts_engine:
            threading.Thread(target=self.falar, args=("Fim de Jogo",)).start()

    def ir_para_welcome(self):
        if self.nickname_box.text.strip():
            self.nickname = self.nickname_box.text.strip()
            self.estado_jogo = "welcome"
            if self.tts_engine:
                threading.Thread(target=self.falar, args=(f"Bem-vindo, {self.nickname}",)).start()

    def reiniciar_jogo(self):
        self.grid = self.criar_grid_vazio()
        self.proximas_pecas.clear(); self.peca_segurada = None; self.pode_segurar = True
        self.score, self.linhas_limpas, self.nivel = 0, 0, 1
        self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[0]
        self.ultimo_tempo_queda = self.tempo_inicio_jogo = time.time()
        self.fim_de_jogo = False; self.pausado = False
        self.gerar_nova_peca()
        self.estado_jogo = "jogando"
        
    def hard_drop(self):
        if self.fim_de_jogo or not self.peca_atual: return
        if self.peca_fantasma:
            distancia = self.peca_fantasma.y - self.peca_atual.y
            self.peca_atual.y = self.peca_fantasma.y
            self.score += distancia * 2
            self.fixar_peca()
            
    def atualizar_nivel_e_score(self, num_linhas_limpas):
        pontos = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += pontos.get(num_linhas_limpas, 0) * self.nivel
        self.linhas_limpas += num_linhas_limpas
        novo_nivel = (self.linhas_limpas // 10) + 1
        if novo_nivel > self.nivel:
            self.nivel = min(novo_nivel, len(config.VELOCIDADES_QUEDA_NIVEL))
            self.intervalo_queda = config.VELOCIDADES_QUEDA_NIVEL[self.nivel - 1]

    def e_espaco_valido(self, peca_teste, deslocamento_x=0, deslocamento_y=0, verificar_rotacao=None):
        coords = peca_teste.obter_coords_forma(rotacao=verificar_rotacao)
        for x, y in coords:
            xf, yf = int(x + deslocamento_x), int(y + deslocamento_y)
            if not (0 <= xf < config.GRID_COLUNAS and yf < config.GRID_LINHAS_TOTAL): return False
            if yf >= 0 and self.grid[yf][xf] != 0: return False
        return True

    def mover_peca(self, dx, dy):
        if self.fim_de_jogo or not self.peca_atual: return False
        if self.e_espaco_valido(self.peca_atual, deslocamento_x=dx, deslocamento_y=dy):
            self.peca_atual.mover(dx, dy)
            self.atualizar_peca_fantasma()
            if self.peca_tocando_chao:
                self.tempo_peca_no_chao = time.time()
            return True
        return False

    def lidar_com_rotacao(self, sentido_horario=True):
        if self.fim_de_jogo or not self.peca_atual: return
        peca = self.peca_atual
        if len(peca.forma) == 1: return
        rotacao_original = peca.rotacao
        rotacao_alvo = (rotacao_original + 1) % len(peca.forma)
        
        testes_deslocamento = [(0, 0)]
        tabela = config.DESLOCAMENTOS_I if peca.nome_forma == 'I' else config.DESLOCAMENTOS_JLSTZ
        chave = (rotacao_original, rotacao_alvo)
        if chave in tabela:
            for dx_srs, dy_srs in tabela[chave]:
                testes_deslocamento.append((dx_srs, -dy_srs))

        for dx, dy in testes_deslocamento:
            if self.e_espaco_valido(peca, dx, dy, verificar_rotacao=rotacao_alvo):
                peca.x += dx; peca.y += dy; peca.rotacao = rotacao_alvo
                self.atualizar_peca_fantasma()
                if self.peca_tocando_chao:
                    self.tempo_peca_no_chao = time.time()
                return

    def segurar_peca(self):
        if self.fim_de_jogo or not self.pode_segurar: return
        self.pode_segurar = False
        if self.peca_segurada is None:
            self.peca_segurada = self.peca_atual
            self.gerar_nova_peca()
        else:
            self.peca_atual, self.peca_segurada = self.peca_segurada, self.peca_atual
        
        self.peca_segurada.rotacao = 0
        self.peca_atual.x = config.GRID_COLUNAS // 2 - 2
        self.peca_atual.y = 0
        
        if not self.e_espaco_valido(self.peca_atual):
            self.finalizar_jogo()
        else:
            self.atualizar_peca_fantasma()

    def atualizar_peca_fantasma(self):
        if not self.peca_atual:
            self.peca_fantasma = None; return
        peca_fantasma_teste = Peca(self.peca_atual.x, self.peca_atual.y, self.peca_atual.nome_forma)
        peca_fantasma_teste.rotacao = self.peca_atual.rotacao
        while self.e_espaco_valido(peca_fantasma_teste, deslocamento_y=1):
            peca_fantasma_teste.mover(0, 1)
        self.peca_fantasma = peca_fantasma_teste

    def gerar_nova_peca(self):
        nomes_formas = list(config.TETROMINOS.keys())
        while len(self.proximas_pecas) < 4:
            nome_forma = random.choice(nomes_formas)
            self.proximas_pecas.append(Peca(config.GRID_COLUNAS // 2 - 2, 0, nome_forma))
        
        self.peca_atual = self.proximas_pecas.pop(0)
        
        if not self.e_espaco_valido(self.peca_atual):
            self.finalizar_jogo()
        else:
            self.atualizar_peca_fantasma()