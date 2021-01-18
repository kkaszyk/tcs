import math
from mem_sys import MemSysComponent
from util import Logger

class ComputeUnit(MemSysComponent):
    def __init__(self, sys, logger_on):
        super().__init__("Compute Unit", sys)
        self.logger = Logger("Compute Unit", logger_on)
        self.waiting_mem = set()

    def load(self, address):
        self.logger.log("Load " + str(address))
        self.lower_load(address)
        self.waiting_mem.add(address)

    def complete_load(self, address):
        cache_line = address >> int(math.log(self.mem_sys.get_cache_line_size()) / math.log(2))        
        clear_addrs = []
        for waiting_address in self.waiting_mem:
            waiting_cache_line = waiting_address >> int(math.log(self.mem_sys.get_cache_line_size()) / math.log(2)) 
            if waiting_cache_line == cache_line:
                self.logger.log(("Data from " + str(waiting_address) + " available."))
                clear_addrs.append(waiting_address)
                
        for address in clear_addrs:
            if address in self.waiting_mem:
                self.waiting_mem.remove(address)
        
    def advance(self, cycles):
        pass
