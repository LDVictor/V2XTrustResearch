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
                print("Selecione uma opcao de cenario para ser simulado: ")
                print("1 - Scenario 1")
                print("2 - Solution 1")
                choice = int(input())
                if choice == 1:
                    with open("scenario1.py") as f1:
                        exec(f1.read())
                else: 
                    with open("solution1.py") as f1:
                        exec(f1.read())

        elif option == 2:
                print("Selecione uma opcao de cenario para ser simulado: ")
                print("1 - Scenario 2")
                print("2 - Solution 2")
                choice = int(input())
                if choice == 1:
                    with open("scenario2.py") as f2:
                        exec(f2.read())
                else:
                    with open("solution2.py") as f2:
                        exec(f2.read())

        elif option == 3:
            with open("scenario3.py") as f3:
                exec(f3.read())
        else:
            option = int(input())

if __name__ == '__main__':
    v2xMenu()
