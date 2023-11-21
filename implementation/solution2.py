import sys
import time
sys.path.insert(0, '..')

# Scenario 2 - Solucao com Autenticacao Distribuida SSI
## Possibilidade de Colisao Conjunta

from resources.vehicle import Vehicle
from resources.fakevehicle import FakeVehicle
from resources.ran import RAN


### Funcoes

def sendMessageToOBU(obu1, obu2, port, message):
    if obu2.verifica_credencial(obu1.vc):
        obu1.send_to_node(port, message)
        print("Mensagem para ", obu2.id, " de ", obu1.id, ": ", message)
        obu2.pendingMessages.append((message, obu1.getName(), obu1.vc))
    else:
        print("Credencial invalida.")

def sendMessageToRAN(obu, ran, port, message_id):
    if ran.verifica_credencial(obu.pendingMessages[message_id][2], obu.pendingMessages[message_id][1]):
        obu.send_to_node(port, obu.pendingMessages[message_id][0])
        print("Mensagem para ", ran.id, " de ", obu.id, ": ", obu.pendingMessages[message_id][0])
        return True
    else:
        print("Credencial invalida (inexistente no VDR).")
        return False
    

debug = False
vehicle_1 = Vehicle("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle("127.0.0.1", 8002, 2)
fake_vehicle = FakeVehicle("127.0.0.1", 8010, 10)
issuer = RAN("127.1.0.1", 8088, 88)
# criando a credencial dos veiculos
vehicle_1.vc = issuer.generate_credential_offer(10, None, 1, None)
vehicle_2.vc = issuer.generate_credential_offer(10, None, 2, None)

print("credencial do vehicle 1: " + str(vehicle_1.vc))
print("credencial do vehicle 2: " + str(vehicle_2.vc))
print("credencial do fake vehicle: " + str(fake_vehicle.vc))

# inicio de simulacao

time.sleep(3)

vehicle_1.start()
fake_vehicle.start()

time.sleep(1)

vehicle_1.debug = debug
fake_vehicle.debug = debug

fake_vehicle.connect_with_node('127.0.0.1', 8001)

time.sleep(2)

message_1 = "ADAS info - Highway X: Empty Traffic && Autobahn"

sendMessageToOBU(fake_vehicle, vehicle_1, 8001, message_1)

time.sleep(2)

print("fake_vehicle: saindo de rota")
fake_vehicle.stop()

time.sleep(5)

enb_ran = RAN("127.0.0.1", 8100, 100)
enb_ran.start()

time.sleep(1)

enb_ran.debug = debug

vehicle_1.connect_with_node("127.0.0.1", 8100)

time.sleep(2)

if sendMessageToRAN(vehicle_1, enb_ran, 8100, 0):

    time.sleep(2)

    print("vehicle 1: saindo de rota")
    vehicle_1.stop()

    time.sleep(5)

    vehicle_2.start()

    time.sleep(1)

    vehicle_2.debug = debug

    enb_ran.connect_with_node('127.0.0.1', 8002)

    time.sleep(2)

    enb_ran.send_to_nodes("ADAS info - Go through Highway X with speed = 130 km/h")

    time.sleep(2)

    print("enb ran: saindo de rota")
    enb_ran.stop()

    print("Fim do Cenario 2")

else:
    print("Fim do Cenario 2")

    sys.exit()


