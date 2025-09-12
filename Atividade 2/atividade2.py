import ZODB, ZODB.FileStorage
import transaction
from persistent import Persistent
from persistent.list import PersistentList

class Livro(Persistent):
    def __init__(self, titulo, autor):
        self.titulo = titulo
        self.autor = autor
        self.emprestado_para = None

class Usuario(Persistent):
    def __init__(self, nome):
        self.nome = nome
        self.livros_emprestados = PersistentList()

def encontrar_livro(root, titulo):
    for livro in root.livros:
        if livro.titulo.lower() == titulo.lower():
            return livro
    return None

def encontrar_usuario(root, nome):
    for usuario in root.usuarios:
        if usuario.nome.lower() == nome.lower():
            return usuario
    return None

def cadastrar_livro(root):
    titulo = input("Digite o título do livro: ")
    if encontrar_livro(root, titulo):
        print(f"\nERRO: Livro com o título '{titulo}' já existe.")
        return
    autor = input("Digite o autor do livro: ")
    novo_livro = Livro(titulo, autor)
    root.livros.append(novo_livro)
    transaction.commit()
    print(f"\nSUCESSO: Livro '{titulo}' cadastrado.")

def cadastrar_usuario(root):
    nome = input("Digite o nome do novo usuário: ")
    if encontrar_usuario(root, nome):
        print(f"\nERRO: Usuário '{nome}' já existe.")
        return
    novo_usuario = Usuario(nome)
    root.usuarios.append(novo_usuario)
    transaction.commit()
    print(f"\nSUCESSO: Usuário '{nome}' cadastrado.")

def registrar_emprestimo(root):
    titulo_livro = input("Digite o título do livro a ser emprestado: ")
    livro = encontrar_livro(root, titulo_livro)
    if not livro:
        print(f"\nERRO: Livro '{titulo_livro}' não encontrado.")
        return
    if livro.emprestado_para is not None:
        print(f"\nERRO: Este livro já está emprestado para {livro.emprestado_para.nome}.")
        return

    nome_usuario = input(f"Digite o nome do usuário para emprestar '{titulo_livro}': ")
    usuario = encontrar_usuario(root, nome_usuario)
    if not usuario:
        print(f"\nERRO: Usuário '{nome_usuario}' não encontrado.")
        return

    livro.emprestado_para = usuario
    usuario.livros_emprestados.append(livro)
    transaction.commit()
    print(f"\nSUCESSO: Livro '{livro.titulo}' emprestado para '{usuario.nome}'.")

def registrar_devolucao(root):
    titulo_livro = input("Digite o título do livro a ser devolvido: ")
    livro = encontrar_livro(root, titulo_livro)
    if not livro:
        print(f"\nERRO: Livro '{titulo_livro}' não encontrado.")
        return
    if livro.emprestado_para is None:
        print("\nERRO: Este livro não está emprestado no momento.")
        return

    usuario = livro.emprestado_para
    
    usuario.livros_emprestados.remove(livro)
    livro.emprestado_para = None
    transaction.commit()
    print(f"\nSUCESSO: Livro '{livro.titulo}' devolvido por '{usuario.nome}'.")

def remover_livro(root):
    titulo = input("Digite o título do livro a ser removido: ")
    livro = encontrar_livro(root, titulo)
    if not livro:
        print(f"\nERRO: Livro '{titulo}' não encontrado.")
        return
    if livro.emprestado_para is not None:
        print(f"\nERRO: Não é possível remover. O livro está emprestado para {livro.emprestado_para.nome}.")
        return

    root.livros.remove(livro)
    transaction.commit()
    print(f"\nSUCESSO: Livro '{titulo}' removido da biblioteca.")

def listar_livros(root):
    print("\n--- LISTA DE LIVROS ---")
    if not root.livros:
        print("Nenhum livro cadastrado.")
    else:
        for livro in root.livros:
            if livro.emprestado_para:
                status = f"Emprestado para: {livro.emprestado_para.nome}"
            else:
                status = "Disponível"
            print(f"- Título: {livro.titulo}, Autor: {livro.autor} (Status: {status})")
    print("-----------------------")

def listar_usuarios(root):
    print("\n--- LISTA DE USUÁRIOS ---")
    if not root.usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        for usuario in root.usuarios:
            print(f"\nUsuário: {usuario.nome}")
            if not usuario.livros_emprestados:
                print("  (Não possui livros emprestados no momento)")
            else:
                print("  Livros emprestados:")
                for livro in usuario.livros_emprestados:
                    print(f"  - {livro.titulo}")
    print("-------------------------")

def main():
    storage = ZODB.FileStorage.FileStorage('biblioteca.fs')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root

    if not hasattr(root, 'livros'):
        root.livros = PersistentList()
    if not hasattr(root, 'usuarios'):
        root.usuarios = PersistentList()
    
    while True:
        print("\n--- Sistema de Biblioteca (ZODB) ---")
        print("1. Cadastrar novo livro")
        print("2. Cadastrar novo usuário")
        print("3. Registrar empréstimo")
        print("4. Registrar devolução")
        print("5. Remover livro")
        print("6. Listar todos os livros")
        print("7. Listar todos os usuários")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            cadastrar_livro(root)
        elif opcao == '2':
            cadastrar_usuario(root)
        elif opcao == '3':
            registrar_emprestimo(root)
        elif opcao == '4':
            registrar_devolucao(root)
        elif opcao == '5':
            remover_livro(root)
        elif opcao == '6':
            listar_livros(root)
        elif opcao == '7':
            listar_usuarios(root)
        elif opcao == '0':
            print("\nSaindo do sistema...")
            break
        else:
            print("\nOpção inválida. Tente novamente.")

    connection.close()
    db.close()

if __name__ == "__main__":
    main()