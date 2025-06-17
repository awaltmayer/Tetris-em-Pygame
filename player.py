# player.py

import config

class Peca:
    def __init__(self, x, y, nome_forma):
        self.x = x 
        self.y = y 
        self.nome_forma = nome_forma
        self.cor = config.TETROMINOS[nome_forma]['cor']
        self.forma = config.TETROMINOS[nome_forma]['forma']
        self.rotacao = 0 

    def mover(self, dx, dy):
        self.x += dx
        self.y += dy

    def obter_coords_forma(self, rotacao=None):

        if rotacao is None:
            rotacao = self.rotacao

        rotacao_real = rotacao % len(self.forma) 
        
        forma_atual = self.forma[rotacao_real]
        
        coords_absolutas = []
        for dx, dy in forma_atual:
            coords_absolutas.append((self.x + dx, self.y + dy))
        return coords_absolutas
