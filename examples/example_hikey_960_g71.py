from system import Sys, MemSysComponent
from compute_unit import ComputeUnit, Core
from cache import Cache
from memory import Memory

sys = Sys("Test Platform", 64)
memory = Memory(sys, 4, 4, 4, 2, 64, 1866, True, None)
l2c = Cache(sys, 1037000, 0, 1, 16, 8, 534288, 64, 3, True, memory.get_component_id())
cores = []
for i in range(8):
    cores.append(Core(i, 3, sys, 1037000, True, l2c.get_component_id()))

sys.build_map()
sys.end_sim()

print(sys.component_map)
memory.print_bandwidth()

cores[0].compute_units[0].load(0x1000)
cores[0].compute_units[1].load(0x1000)

baseaddr = 0x1100
for i in range(16):
    cores[1].compute_units[0].load(baseaddr + 0x100*i)
    
i = 0
while i < 5:
    sys.advance(1)
    i += 1

cores[2].compute_units[2].load(0x1000)
i = 0
while i < 5:
    sys.advance(1)
    i += 1

cores[2].compute_units[1].load(0x1001)

i = 0
while i < 5:
    sys.advance(1)
    i += 1

cores[4].compute_units[0].load(0x1002)
i = 0
while i < 150:
    sys.advance(1)
    i += 1

sys.printclks()
