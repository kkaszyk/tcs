import math

from mem_sys import MemSysComponent
from util import Logger

class MSHRBank():
    def __init__(self, num_regs):
        self.num_regs = num_regs
        self.mshrs = []

    def isInMSHR(self, address):
        return address in self.mshrs
        
    def isMSHRAvailable(self):
        return len(self.mshrs) < self.num_regs
    
    def write(self,address):
        for addr in self.mshrs:
            if addr == address:
                return
    
        self.mshrs.append(address)

    def clear(self,address):
        return self.mshrs.remove(address)

class Cache(MemSysComponent):
    def __init__(self, sys, clk, user_id, level, num_mshrs, cache_size, line_size, latency, logger_on, lower_component):
        super().__init__("L" + str(level) + " Cache " + str(user_id), clk, sys, lower_component)
        self.level = level
        self.num_mshrs = num_mshrs
        self.active_queue = []
        self.stall_queue = []
        self.mshr_bank = MSHRBank(self.num_mshrs)
        self.logger = Logger(self.name, logger_on, self.mem_sys)
        
        # Cache Configuration
        self.tlb_size = 32
        self.cache_size = cache_size
        self.line_size = line_size
        self.max_size = self.cache_size / self.line_size
        self.latency = latency

        self.accesses = []
        self.cache = [0,0]
        self.mem_queue = []
        
    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
        cache_line = address >> int(math.log(self.line_size) / math.log(2))
        hit = False

        for line in self.accesses:
            if line == cache_line:
                self.cache[0] += 1
                self.accesses.remove(cache_line)
                self.accesses.insert(0,cache_line)
                hit = True
                break
        
        if hit:
            self.logger.log("Hit " + str(hex(address)))
            self.mem_queue.append([address, self.latency])
        elif self.mshr_bank.isInMSHR(cache_line):
            self.logger.log("Already waiting on memory access to cache line " + str(hex(cache_line)) + ".")
        else:
            self.logger.log("Miss " + str(hex(cache_line)))
            if self.mshr_bank.isMSHRAvailable():
                self.mshr_bank.write(cache_line)
                self.lower_load(address)
            else:
                self.logger.log("Stall " + str(hex(address)))
                self.stall_queue.append(address)

    def complete_load(self, address):
        cache_line = address >> int(math.log(self.line_size) / math.log(2))

        if self.mshr_bank.isInMSHR(cache_line):
            self.mshr_bank.clear(cache_line)

            for line in self.accesses:
                if line == cache_line:
                    self.accesses.remove(cache_line)
                    break

            self.accesses.insert(0, cache_line)
        self.mem_queue.append([address, self.latency])

        while self.mshr_bank.isMSHRAvailable() and len(self.stall_queue) > 0:
            self.load(self.stall_queue.pop(0))
                
    def advance(self, cycles):
        self.clk += cycles
        self.logger.log(self.mem_queue)
        remove_list = []
        
        for i in range(len(self.mem_queue)):
            self.mem_queue[i][1] -= cycles

            if self.mem_queue[i][1] <= 0:
                self.logger.log("Handing over to " + self.mem_sys.hierarchy[self.mem_sys_component_id-1].name + ".")

                cache_line = self.mem_queue[i][0] >> int(math.log(self.line_size) / math.log(2))
                self.return_load(self.mem_queue[i][0])
                    
                remove_list.append(i)

        remove_list.reverse()
        for i in remove_list:
            self.mem_queue.pop(i)