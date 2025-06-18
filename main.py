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

    while jogo.rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo.rodando = False

            if jogo.estado_jogo == "menu":
                retorno_input = jogo.nickname_box.handle_event(evento)
                if retorno_input == "enter":
                    jogo.ir_para_welcome()
            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_pos = evento.pos
                if jogo.estado_jogo == "menu":
                    if jogo.botoes_menu_principal["iniciar"].collidepoint(mouse_pos):
                        jogo.ir_para_welcome()
                    elif jogo.botoes_menu_principal["sair"].collidepoint(mouse_pos):
                        jogo.rodando = False
                
                elif jogo.estado_jogo == "welcome":
                    if jogo.botao_iniciar_welcome.collidepoint(mouse_pos):
                        jogo.reiniciar_jogo()

                elif jogo.estado_jogo == "fim_de_jogo":
                    botoes_config = {"Reiniciar": config.RECT_GAMEOVER_BOTAO_REINICIAR, "Menu Principal": config.RECT_GAMEOVER_BOTAO_MENU}
                    if botoes_config["Reiniciar"].collidepoint(mouse_pos):
                        jogo.reiniciar_jogo()
                    elif botoes_config["Menu Principal"].collidepoint(mouse_pos):
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