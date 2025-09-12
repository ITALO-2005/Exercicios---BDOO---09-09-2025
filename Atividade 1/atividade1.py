import ZODB, ZODB.FileStorage
import transaction
from persistent import Persistent
from persistent.list import PersistentList

class Produto(Persistent):
    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade

    def __str__(self):
        return f"Produto: {self.nome}, Quantidade: {self.quantidade}"

class Estoque(Persistent):
    def __init__(self):
        self.produtos = PersistentList()

    def find_produto(self, nome):
        """Busca um produto pelo nome e retorna o objeto se encontrado."""
        for produto in self.produtos:
            if produto.nome.lower() == nome.lower():
                return produto
        return None

    def adicionar_produto(self, nome, quantidade):
        """Adiciona um novo produto ao estoque, evitando duplicatas."""
        if self.find_produto(nome):
            print(f"\nERRO: O produto '{nome}' já existe no estoque.")
            return False
        
        if quantidade < 0:
            print("\nERRO: A quantidade inicial não pode ser negativa.")
            return False

        novo_produto = Produto(nome, quantidade)
        self.produtos.append(novo_produto)
        print(f"\nSUCESSO: Produto '{nome}' adicionado com {quantidade} unidades.")
        return True

    def listar_produtos(self):
        print("\n--- LISTA DE PRODUTOS NO ESTOQUE ---")
        if not self.produtos:
            print("O estoque está vazio.")
        else:
            for produto in self.produtos:
                print(f"- {produto.nome}: {produto.quantidade} unidades")
        print("------------------------------------")

    def adicionar_quantidade(self, nome, quantidade_adicionar):
        produto = self.find_produto(nome)
        if not produto:
            print(f"\nERRO: Produto '{nome}' não encontrado.")
            return False
        
        if quantidade_adicionar <= 0:
            print("\nERRO: A quantidade a ser adicionada deve ser positiva.")
            return False
        
        produto.quantidade += quantidade_adicionar
        print(f"\nSUCESSO: {quantidade_adicionar} unidades adicionadas ao produto '{nome}'. Novo total: {produto.quantidade}.")
        return True

    def remover_quantidade(self, nome, quantidade_remover):
        produto = self.find_produto(nome)
        if not produto:
            print(f"\nERRO: Produto '{nome}' não encontrado.")
            return False

        if quantidade_remover <= 0:
            print("\nERRO: A quantidade a ser removida deve ser positiva.")
            return False

        if produto.quantidade < quantidade_remover:
            print(f"\nERRO: Operação inválida. Estoque atual ({produto.quantidade}) é insuficiente para remover {quantidade_remover} unidades.")
            return False
        
        produto.quantidade -= quantidade_remover
        print(f"\nSUCESSO: {quantidade_remover} unidades removidas do produto '{nome}'. Novo total: {produto.quantidade}.")
        return True
        
    def remover_produto_do_estoque(self, nome):
        produto = self.find_produto(nome)
        if not produto:
            print(f"\nERRO: Produto '{nome}' não encontrado.")
            return False
            
        self.produtos.remove(produto)
        print(f"\nSUCESSO: Produto '{nome}' foi removido do estoque.")
        return True

def mostrar_menu():
    """Exibe o menu de opções para o usuário."""
    print("\n--- Sistema de Gerenciamento de Estoque (ZODB) ---")
    print("1. Adicionar novo produto")
    print("2. Buscar produto por nome")
    print("3. Listar todos os produtos")
    print("4. Adicionar quantidade a um produto")
    print("5. Remover quantidade de um produto")
    print("6. Remover produto do estoque")
    print("0. Sair")

def main():
    storage = ZODB.FileStorage.FileStorage('estoque.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root

    if not hasattr(root, 'estoque'):
        root.estoque = Estoque()
        transaction.commit()
    
    estoque = root.estoque

    while True:
        mostrar_menu()
        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("\nERRO: Por favor, insira um número válido.")
            continue

        if opcao == 1:
            nome = input("Digite o nome do novo produto: ")
            try:
                quantidade = int(input(f"Digite a quantidade inicial de '{nome}': "))
                if estoque.adicionar_produto(nome, quantidade):
                    transaction.commit()
            except ValueError:
                print("\nERRO: Quantidade inválida. Por favor, insira um número inteiro.")

        elif opcao == 2:
            nome = input("Digite o nome do produto a ser buscado: ")
            produto = estoque.find_produto(nome)
            if produto:
                print("\n--- DETALHES DO PRODUTO ---")
                print(produto)
                print("---------------------------")
            else:
                print(f"\nProduto '{nome}' não encontrado no estoque.")

        elif opcao == 3:
            estoque.listar_produtos()

        elif opcao == 4:
            nome = input("Digite o nome do produto para adicionar quantidade: ")
            try:
                quantidade = int(input(f"Digite a quantidade a ser ADICIONADA para '{nome}': "))
                if estoque.adicionar_quantidade(nome, quantidade):
                    transaction.commit()
            except ValueError:
                print("\nERRO: Quantidade inválida. Por favor, insira um número inteiro.")
        
        elif opcao == 5:
            nome = input("Digite o nome do produto para remover quantidade: ")
            try:
                quantidade = int(input(f"Digite a quantidade a ser REMOVIDA de '{nome}': "))
                if estoque.remover_quantidade(nome, quantidade):
                    transaction.commit()
            except ValueError:
                print("\nERRO: Quantidade inválida. Por favor, insira um número inteiro.")

        elif opcao == 6:
            nome = input("Digite o nome do produto a ser REMOVIDO do estoque: ")
            confirmacao = input(f"Tem certeza que deseja remover '{nome}' permanentemente? (s/n): ").lower()
            if confirmacao == 's':
                if estoque.remover_produto_do_estoque(nome):
                    transaction.commit()
            else:
                print("\nOperação cancelada.")

        elif opcao == 0:
            print("\nSaindo do sistema...")
            break
        
        else:
            print("\nERRO: Opção inválida. Tente novamente.")

    connection.close()
    db.close()

if __name__ == "__main__":
    main()