# V2XTrustResearch

def v2xMenu():
    print("V2XTrustResearch Menu")
    print()
    print("Selecione uma opcao de cenario para ser simulado: ")
    print("1 - Cenario 1")
    print("2 - Cenario 2")
    print("3 - Cenario 3")
    print("0 - Sair")
    option = int(input())

    while (option != 0):
        if option == 1:
            with open("scenario1.py") as f:
                exec(f.read())
            option = int(input())
        elif option == 2:
            print("")
            option = int(input())
        elif option == 3:
            print("")
            option = int(input())
        else:
            option = int(input())

if __name__ == '__main__':
    v2xMenu()

