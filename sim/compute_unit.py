import math
from mem_sys import MemSysComponent
from util import Logger

class ComputeUnit(MemSysComponent):
    def __init__(self, sys, clk, user_id, logger_on, lower_component):
        super().__init__("Compute Unit " + str(user_id), clk, sys, lower_component)
        self.logger = Logger(self.name, logger_on, self.mem_sys)
        self.waiting_mem = set()

    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
        self.lower_load(address)
        self.waiting_mem.add(address)
        self.is_idle = False

    def complete_load(self, address):
        cache_line = address >> int(math.log(self.mem_sys.get_cache_line_size()) / math.log(2))        
        clear_addrs = []
        for waiting_address in self.waiting_mem:
            waiting_cache_line = waiting_address >> int(math.log(self.mem_sys.get_cache_line_size()) / math.log(2)) 
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
