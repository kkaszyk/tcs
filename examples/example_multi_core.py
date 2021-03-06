from system import Sys, MemSysComponent
from compute_unit import ComputeUnit
from cache import Cache
from memory import Memory

sys = Sys("Test Platform", 64)
memory = Memory(sys, 4, 4, 4, 2, 64, 1866, True, None)
l2c = Cache(sys, 1037000, 0, 1, 16, 8, 534288, 64, 3, True, memory.get_component_id())
l1c0 = Cache(sys, 1037000, 0, 0, 16, 8, 16384, 64, 1, True, l2c.get_component_id())
l1c1 = Cache(sys, 1037000, 1, 0, 16, 8, 16384, 64, 1, True, l2c.get_component_id())
cu0 = ComputeUnit(sys, 1037000, 0, True, l1c0.get_component_id())
cu1 = ComputeUnit(sys, 1037000, 1, True, l1c1.get_component_id())

sys.build_map()
sys.end_sim()

print(sys.component_map)
memory.print_bandwidth()

cu0.load(0x1000)
cu1.load(0x1000)

baseaddr = 0x1100
for i in range(16):
    cu0.load(baseaddr + 0x100*i)
    
i = 0
while i < 5:
    sys.advance(1)
    i += 1

cu0.load(0x1000)
i = 0
while i < 5:
    sys.advance(1)
    i += 1

cu0.load(0x1001)

i = 0
while i < 5:
    sys.advance(1)
    i += 1

cu0.load(0x1002)
i = 0
while i < 150:
    sys.advance(1)
    i += 1

sys.printclks()
