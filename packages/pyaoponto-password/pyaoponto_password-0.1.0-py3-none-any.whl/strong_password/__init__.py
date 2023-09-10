from .generator import gerar_senha

def main():
    tamanho = int(input("Tamanho desejado da senha (mínimo 6): "))
    senha = gerar_senha(tamanho)
    if senha:
        print("Senha gerada:", senha)
