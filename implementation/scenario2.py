import sys
import time
sys.path.insert(0, '..')

# Scenario 2
## Possibilidade de Colisao Conjunta

from resources.vehicle import Vehicle
from resources.fakevehicle import FakeVehicle
from resources.ran import RAN

debug = False
vehicle_1 = Vehicle("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle("127.0.0.1", 8002, 2)
fake_vehicle = FakeVehicle("127.0.0.1", 8010, 10)
enb_ran = RAN("127.0.0.1", 8100, 100)

time.sleep(3)

vehicle_1.start()
fake_vehicle.start()

time.sleep(1)

vehicle_1.debug = debug
fake_vehicle.debug = debug

fake_vehicle.connect_with_node('127.0.0.1', 8001)

time.sleep(2)

fake_vehicle.send_to_node(8001, "ADAS info - Highway X: Empty Traffic && Autobahn")

time.sleep(2)

print("fake_vehicle: saindo de rota")
fake_vehicle.stop()

time.sleep(5)

enb_ran.start()

time.sleep(1)

enb_ran.debug = debug

vehicle_1.connect_with_node("127.0.0.1", 8100)

time.sleep(2)

vehicle_1.send_to_node(8100, "ADAS info - Highway X: Empty Traffic && Autobahn")

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