import math
from system import MemSysComponent
from util import Logger
from cache import Cache
from component import SchedComponent

class ComputeUnit(MemSysComponent):
    def __init__(self, sys, clk, user_id, logger_on, lower_component):
        super().__init__("Compute Unit " + str(user_id), clk, sys, lower_component)
        self.logger = Logger(self.name, logger_on, self.sys)
        self.waiting_mem = set()
        self.store_queue = []

    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
        self.lower_load(address)
        self.waiting_mem.add(address)
        self.is_idle = False

    def store(self, address):
        self.logger.log("Store " + str(hex(address)))
        self.lower_store(address)
        
    def complete_load(self, address):
        cache_line = address >> int(math.log(self.sys.get_cache_line_size()) / math.log(2))        
        clear_addrs = []
        for waiting_address in self.waiting_mem:
            waiting_cache_line = waiting_address >> int(math.log(self.sys.get_cache_line_size()) / math.log(2)) 
            if waiting_cache_line == cache_line:
                self.logger.log(("Data from " + str(hex(waiting_address)) + " available."))
                clear_addrs.append(waiting_address)
                
        for address in clear_addrs:
            if address in self.waiting_mem:
                self.waiting_mem.remove(address)

        if len(self.waiting_mem) == 0:
            self.is_idle = True

    def advance(self, cycles):
        self.clk += cycles

class Core(SchedComponent):
    def __init__(self, core_id, num_compute_units, sys, clk, logger_on, lower_compute_id, lower_mem_id):
        super().__init__("Core", clk, sys, lower_compute_id)
        self.core_id = core_id
        self.compute_units = []
        self.l1c = Cache(sys, clk, core_id, 0, 16, 8, 16384, 64, 1, logger_on, lower_mem_id)
        for i in range(num_compute_units):
            self.compute_units.append(ComputeUnit(sys, clk, i, logger_on, self.l1c.get_component_id()))
