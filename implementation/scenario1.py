import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

from resources.vehicle1 import Vehicle1
from resources.fakevehicle import FakeVehicle
from resources.ran import RAN

vehicle_1 = Vehicle1("127.0.0.1", 8001, 1)
vehicle_2 = Vehicle1("127.0.0.1", 8002, 2)
fake_vehicle = FakeVehicle("127.0.0.1", 8003, 3)
enb_ran = RAN("127.0.0.1", 8100, 100)

time.sleep(3)

vehicle_1.start()
vehicle_2.start()
fake_vehicle.start()

time.sleep(1)

debug = False
vehicle_1.debug = debug
vehicle_2.debug = debug
fake_vehicle.debug = debug

fake_vehicle.connect_with_node('127.0.0.1', 8001)

time.sleep(2)

fake_vehicle.send_to_nodes("ADAS message - Highway X: Heavy Traffic")
fake_vehicle.send_to_nodes("ADAS message - Highway Y: Empty Traffic")

time.sleep(2)

print("fake_vehicle: saindo de rota")
fake_vehicle.stop()

print("Fim do Cenario 1")


