import unittest
from cache import Cache
from memory import Memory
from compute_unit import ComputeUnit
from mem_sys import MemSys, MemSysComponent

class TestCache(unittest.TestCase):

    def setUp(self):
        self.sys = MemSys("Test Platform", 64)
        self.memory = Memory(self.sys, 4, 4, 4, 2, 64, 1866, True, None)
        self.l2c = Cache(self.sys, 1037000, 0, 1, 16, 8, 534288, 64, 3, True, self.memory.get_component_id())
        self.l1c0 = Cache(self.sys, 1037000, 0, 0, 16, 8, 16384, 64, 1, True, self.l2c.get_component_id())
        self.cu0 = ComputeUnit(self.sys, 1037000, 0, True, self.l1c0.get_component_id())
        self.sys.build_map()
        
    def test_cache_line_addr_calc(self):
        self.assertEqual(self.l1c0.get_cache_line(0x4000), 0x100)
        self.assertEqual(self.l1c0.get_cache_line(0x4010), 0x100)
        self.assertEqual(self.l1c0.get_cache_line(0x4110), 0x104)
        self.assertEqual(self.l1c0.get_cache_line(0x4112), 0x104)
        self.assertEqual(self.l1c0.get_cache_line(0x41100000), 0x1044000)
        self.assertEqual(self.l1c0.get_cache_line(0x4110000000000000), 0x104400000000000)
