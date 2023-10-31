import sys
import time
sys.path.insert(0, '..')

# Scenario 3
## Omissao de Pos-colisao

from resources.vehicle import Vehicle
from resources.fakevehicle import FakeVehicle
from resources.ran import RAN

debug = False
vehicle_1 = Vehicle("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle("127.0.0.1", 8002, 2)
vehicle_3 = Vehicle("127.0.0.1", 8003, 3)
vehicle_4 = Vehicle("127.0.0.1", 8004, 4)
vehicle_5 = Vehicle("127.0.0.1", 8005, 5)
fake_vehicle = FakeVehicle("127.0.0.1", 8010, 10)
enb_ran = RAN("127.0.0.1", 8100, 100)

time.sleep(3)

vehicle_1.start()
fake_vehicle.start()

time.sleep(1)

vehicle_1.debug = debug
fake_vehicle.debug = debug

vehicle_1.connect_with_node('127.0.0.1', 8010)

time.sleep(2)

vehicle_1.send_to_node(8010, "ADAS info - Highway X: Post Crash Notification -> Call Emergency Vehicles")

time.sleep(2)

print("vehicle 1: saindo de rota")
vehicle_1.stop()

time.sleep(5)

vehicle_2.start()

time.sleep(1)

vehicle_2.debug = debug

fake_vehicle.connect_with_node("127.0.0.2", 8002)

time.sleep(2)

fake_vehicle.send_to_node(8002, "ADAS info - Highway X: Empty Traffic")

time.sleep(2)

print("fake vehicle: saindo de rota")
fake_vehicle.stop()

time.sleep(5)

enb_ran.start()

time.sleep(1)

enb_ran.debug = debug

vehicle_2.connect_with_node('127.0.0.1', 8100)

time.sleep(2)

vehicle_2.send_to_node(8100, "ADAS info - Highway X: Empty Traffic")

time.sleep(2)

print("vehicle 2: saindo de rota")
vehicle_2.stop()

time.sleep(5)

vehicle_3.start()
vehicle_4.start()
vehicle_5.start()

time.sleep(1)

vehicle_3.debug = debug
vehicle_4.debug = debug
vehicle_5.debug = debug

enb_ran.connect_with_node('127.0.0.1', 8003)
enb_ran.connect_with_node('127.0.0.1', 8004)
enb_ran.connect_with_node('127.0.0.1', 8005)

time.sleep(2)

enb_ran.send_to_nodes("ADAS info - Go through Highway X")

time.sleep(2)

print("enb ran: saindo de rota")
enb_ran.stop()

print("Fim do Cenario 3")