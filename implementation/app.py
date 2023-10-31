# V2XTrustResearch

def v2xMenu():
    print("V2XTrustResearch Menu")
    print()
    print("Selecione uma opcao de cenario para ser simulado: ")
    print("1 - Desvio de Trafego Veicular")
    print("2 - Possibilidade de Colisao Conjunta")
    print("3 - Omissao de Pos-colisao")
    print("0 - Sair")
    option = int(input())

    while (option != 0):
        if option == 1:
            with open("scenario1.py") as f:
                exec(f.read())
        elif option == 2:
            with open("scenario2.py") as f:
                exec(f.read())
        elif option == 3:
            with open("scenario3.py") as f:
                exec(f.read())
        else:
            option = int(input())

if __name__ == '__main__':
    v2xMenu()

