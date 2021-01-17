from mem_sys import MemSys, MemSysComponent
from compute_unit import ComputeUnit
from cache import Cache
from memory import Memory

sys = MemSys("Test Platform", 64)
ee = ComputeUnit(sys, True)
l1c = Cache(sys, 0, 6, 16384, 64, 1, True)
l2c = Cache(sys, 1, 6, 534288, 64, 3, True)
caches = [l1c, l2c]
memory = Memory(sys, 10, True)

sys.set_hierarchy([ee,l1c,l2c,memory])

ee.load(0x1000)

i = 0
while i < 5:
    sys.advance(1)
    i += 1

ee.load(0x1000)
i = 0
while i < 5:
    sys.advance(1)
    i += 1

ee.load(0x1001)

i = 0
while i < 5:
    sys.advance(1)
    i += 1

ee.load(0x1002)
i = 0
while i < 5:
    sys.advance(1)
    i += 1
