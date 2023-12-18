import sys
import time
sys.path.insert(0, '..')

# Scenario 3 - Solucao com Autenticacao Distribuida SSI
## Omissao de Pos-colisao

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
collided_vehicles = Vehicle("127.0.0.1", 8008, 8)
vehicle_1 = Vehicle("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle("127.0.0.1", 8002, 2)
ambulance = Vehicle("127.0.0.1", 8003, 3)
fake_vehicle = FakeVehicle("127.0.0.1", 8010, 10)
issuer = RAN("127.1.0.1", 8088, 88)    
# criando a credencial dos veiculos
start_1 = time.perf_counter()
vehicle_1.vc = issuer.generate_credential_offer(10, None, 1, None)
vehicle_2.vc = issuer.generate_credential_offer(10, None, 2, None)
ambulance.vc = issuer.generate_credential_offer(10, None, 3, None)
collided_vehicles.vc = issuer.generate_credential_offer(10, None, 8, None)
end_1 = time.perf_counter()

print("credencial do no 'collided_vehicles': " + str(collided_vehicles.vc))
print("credencial do vehicle 1: " + str(vehicle_1.vc))
print("credencial do vehicle 2: " + str(vehicle_2.vc))
print("credencial da ambulancia: " + str(ambulance.vc))
print("credencial do fake vehicle: " + str(fake_vehicle.vc))

# inicio de simulacao

time.sleep(3)

collided_vehicles.start()
fake_vehicle.start()

time.sleep(1)

collided_vehicles.debug = debug
fake_vehicle.debug = debug

collided_vehicles.connect_with_node('127.0.0.1', 8010)

time.sleep(2)

message_1 = "ADAS info - Highway X: Post Crash Notification -> Call Emergency Vehicles"

start_2 = time.perf_counter()
sendMessageToOBU(collided_vehicles, fake_vehicle, 8010, message_1)
end_2 = time.perf_counter()

time.sleep(2)

vehicle_1.start()

time.sleep(1)

vehicle_1.debug = debug

fake_vehicle.connect_with_node('127.0.0.1', 8001)

time.sleep(2)

message_2 = "ADAS info - Highway X: Empty Traffic"

start_3 = time.perf_counter()
sendMessageToOBU(fake_vehicle, vehicle_1, 8001, message_2)
end_3 = time.perf_counter()

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

start_4 = time.perf_counter()
if sendMessageToRAN(vehicle_1, enb_ran, 8100, 0):

    time.sleep(2)

    print("ameaca ocorrida.")

else:
    end_4 = time.perf_counter()

    collided_vehicles.connect_with_node("127.0.0.1", 8001)
    sendMessageToOBU(collided_vehicles, vehicle_1, 8001, message_1)

    vehicle_1.send_to_node(8100, "ADAS info - Highway X: Post Crash Notification -> Call Emergency Vehicles")

    vehicle_1.stop()

    vehicle_2.start()
    ambulance.start()

    enb_ran.connect_with_node("127.0.0.1", 8002)
    enb_ran.connect_with_node("127.0.0.1", 8003)

    enb_ran.send_to_nodes("ADAS info - Call Emergency Vehicles")

    print("Fim do Cenario 3")

    print("Tempo da criacao de VCs pelo issuer e registro na Wallet de dados dos veiculos: ", (end_1 - start_1) * 100)

    print("Tempo da transmissao da mensagem do collided_vehicles sem verificacao de VC: ", (end_2 - start_2) * 100)

    print("Tempo da transmissao da mensagem do fake_vehicle com verificacao de VC: ", (end_3 - start_3) * 100)

    print("Tempo da transmissao da mensagem p/ RAN c/ verificacao de VC: ", (end_4 - start_4) * 100)

    sys.exit()