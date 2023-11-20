import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

# Scenario 1 - Solucao com Autenticacao Distribuida SSI
## Desvio de Trafego Veicular

from resources.vehicle import Vehicle
from resources.fakevehicle import FakeVehicle
from resources.ran import RAN

debug = False

# gerando as credenciais dos veiculos
vehicle_1 = Vehicle("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle("127.0.0.1", 8002, 2)
vehicle_3 = Vehicle("127.0.0.1", 8003, 3)
vehicle_4 = Vehicle("127.0.0.1", 8004, 4)
fake_vehicle = FakeVehicle("127.0.0.1", 8010, 10)
issuer = RAN("127.1.0.1", 8088, 88)
# criando a credencial dos veiculos
vehicle_1.vc = issuer.generate_credential_offer(10, None, 1, None)
vehicle_2.vc = issuer.generate_credential_offer(10, None, 2, None)
vehicle_3.vc = issuer.generate_credential_offer(10, None, 3, None)
vehicle_4.vc = issuer.generate_credential_offer(10, None, 4, None)

print("credencial do vehicle 1: " + str(vehicle_1.vc))
print("credencial do vehicle 2: " + str(vehicle_2.vc))
print("credencial do vehicle 3: " + str(vehicle_3.vc))
print("credencial do vehicle 4: " + str(vehicle_4.vc))
print("credencial do fake vehicle: " + str(fake_vehicle.vc))

# inicio da simulacao

time.sleep(3)

vehicle_1.start()
fake_vehicle.start()

time.sleep(1)

vehicle_1.debug = debug
fake_vehicle.debug = debug

fake_vehicle.connect_with_node('127.0.0.1', 8001)

time.sleep(2)
message_1 = "ADAS info - Highway X: Heavy Traffic"
message_2 = "ADAS info - Highway Y: Empty Traffic"

if vehicle_1.verifica_credencial(fake_vehicle.vc):
    fake_vehicle.send_to_node(8001, message_1)
    print("Mensagem (1) de 10: " + message_1)
    fake_vehicle.send_to_node(8001, message_2)
    print("Mensagem (1) de 10: " + message_2)
    vehicle_1.pendingMessages.append((message_1, fake_vehicle.getName(), fake_vehicle.vc))
    vehicle_1.pendingMessages.append((message_2, fake_vehicle.getName(), fake_vehicle.vc))

time.sleep(2)

print("fake_vehicle: saindo de rota")
fake_vehicle.stop()

time.sleep(5)

enb_ran = RAN("127.0.0.2", 8008, 8)
enb_ran.start()

time.sleep(1)

enb_ran.debug = debug

vehicle_1.connect_with_node("127.0.0.2", 8008)

time.sleep(2)

if enb_ran.verifica_credencial(fake_vehicle.vc, fake_vehicle.id):
    vehicle_1.send_to_node(8008, vehicle_1.pendingMessages[0][0])
    print("Mensagem (8) de 1: " + vehicle_1.pendingMessages[0][0])
    vehicle_1.send_to_node(8008, vehicle_1.pendingMessages[1][0])
    print("Mensagem (8) de 1: " + vehicle_1.pendingMessages[1][0])

    time.sleep(2)

    print("vehicle 1: saindo de rota")
    vehicle_1.stop()

    time.sleep(5)


    vehicle_2.start()
    vehicle_3.start()
    vehicle_4.start()

    time.sleep(1)

    vehicle_2.debug = debug
    vehicle_3.debug = debug
    vehicle_4.debug = debug

    enb_ran.connect_with_node('127.0.0.1', 8002)
    enb_ran.connect_with_node('127.0.0.1', 8003)
    enb_ran.connect_with_node('127.0.0.1', 8004)

    time.sleep(2)

    enb_ran.send_to_nodes("ADAS info - Go through Highway Y")

    time.sleep(2)

    print("enb ran: saindo de rota")
    enb_ran.stop()

    print("Fim do Cenario 1")

    sys.exit()

else:
    print("Credencial invalida (inexistente no VDR).")
    print("Fim do Cenario 1")

    sys.exit()