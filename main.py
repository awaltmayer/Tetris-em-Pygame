import pygame
import sys
import time
import config
from game import Tetris

def main():
    pygame.init()
    pygame.font.init()

    tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
    pygame.display.set_caption("TETRIZOS")
    relogio = pygame.time.Clock()

    jogo = Tetris(tela)

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if jogo.estado_jogo == "menu":
                retorno_input = jogo.nickname_box.handle_event(evento)
                if retorno_input == "enter":
                    if jogo.nickname_box.text.strip():
                        jogo.reiniciar_jogo()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_pos = evento.pos
                if jogo.estado_jogo == "menu":
                    if jogo.botoes_menu_principal["iniciar"].collidepoint(mouse_pos):
                        if jogo.nickname_box.text.strip():
                            jogo.reiniciar_jogo()
                    elif jogo.botoes_menu_principal["sair"].collidepoint(mouse_pos):
                        rodando = False

                elif jogo.estado_jogo == "fim_de_jogo":
                    if "Reiniciar" in jogo.botoes_fim_de_jogo_rects and jogo.botoes_fim_de_jogo_rects["Reiniciar"].collidepoint(mouse_pos):
                        jogo.reiniciar_jogo()
                    elif "Menu Principal" in jogo.botoes_fim_de_jogo_rects and jogo.botoes_fim_de_jogo_rects["Menu Principal"].collidepoint(mouse_pos):
                        jogo.estado_jogo = "menu"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and jogo.estado_jogo == "jogando":
                    jogo.pausado = not jogo.pausado
                
                if jogo.estado_jogo == "jogando" and not jogo.pausado:
                    if evento.key == pygame.K_LEFT:
                        jogo.move_esquerda_pressionado = True
                        jogo.tempo_inicial_das = time.time() * 1000
                        jogo.ultimo_tempo_arr = jogo.tempo_inicial_das
                        jogo.mover_peca(-1, 0)
                    elif evento.key == pygame.K_RIGHT:
                        jogo.move_direita_pressionado = True
                        jogo.tempo_inicial_das = time.time() * 1000
                        jogo.ultimo_tempo_arr = jogo.tempo_inicial_das
                        jogo.mover_peca(1, 0)
                    elif evento.key == pygame.K_DOWN:
                        jogo.queda_suave_pressionado = True
                    elif evento.key == pygame.K_UP:
                        jogo.lidar_com_rotacao()
                    elif evento.key == pygame.K_c:
                        jogo.segurar_peca()
                    elif evento.key == pygame.K_RETURN:
                        jogo.hard_drop()

            if evento.type == pygame.KEYUP:
                if jogo.estado_jogo == "jogando" and not jogo.pausado:
                    if evento.key == pygame.K_LEFT:
                        jogo.move_esquerda_pressionado = False
                    elif evento.key == pygame.K_RIGHT:
                        jogo.move_direita_pressionado = False
                    elif evento.key == pygame.K_DOWN:
                        jogo.queda_suave_pressionado = False
    
        jogo.atualizar()
        jogo.desenhar()

        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()