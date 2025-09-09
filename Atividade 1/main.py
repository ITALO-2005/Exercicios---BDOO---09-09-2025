import ZODB
import persistent

class produto(persistent. Persistent):
    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade

    def adicionar_novo_produto(self, novoproduto):
        pass

    def buscar_produto(self, buscarproduto):
        pass

        






