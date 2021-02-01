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
    def __init__(self, sys, clk, user_id, level, num_load_mshrs, num_parallel_stores, cache_size, line_size, latency, logger_on, lower_component):
        super().__init__("L" + str(level) + " Cache " + str(user_id), clk, sys, lower_component)
        self.level = level
        self.num_load_mshrs = num_load_mshrs
        self.num_parallel_stores = num_parallel_stores
        self.load_stall_queue = []
        self.store_stall_queue = []
        self.load_mshr_bank = MSHRBank(self.num_load_mshrs)
        self.logger = Logger(self.name, logger_on, self.sys)
        
        # Cache Configuration
        self.tlb_size = 32
        self.cache_size = cache_size
        self.line_size = line_size
        self.max_size = self.cache_size / self.line_size
        self.latency = latency

        self.accesses = []
        self.cache = [0,0]
        self.load_queue = []
        self.store_queue = []

        self.offset_bits = int(math.log2(self.line_size))
        self.word_size = 64
        self.byte_addressable = True

    def get_cache_line(self, address):
        return address >> self.offset_bits
    
    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
        self.is_idle = False
        cache_line = self.get_cache_line(address)
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
            self.load_queue.append([address, self.latency])
        elif self.load_mshr_bank.isInMSHR(cache_line):
            self.logger.log("Already waiting on memory access to cache line " + str(hex(cache_line)) + ".")
        else:
            self.logger.log("Miss " + str(hex(cache_line)))
            if self.load_mshr_bank.isMSHRAvailable():
                self.load_mshr_bank.write(cache_line)
                self.lower_load(address)
            else:
                self.logger.log("Stall " + str(hex(address)))
                self.load_stall_queue.append(address)

    def store(self, address):
        self.logger.log("Store " + str(hex(address)))
        self.is_idle = False
        if len(self.store_queue) < self.num_parallel_stores:
            self.store_queue.append([address, self.latency])
        else:
            self.store_stall_queue.append(address)
        
    def complete_store(self, address):
        cache_line = self.get_cache_line(address)
        hit = False

        for line in self.accesses:
            if line == cache_line:
                self.cache[0] += 1
                self.accesses.remove(cache_line)
                self.accesses.insert(0,cache_line)
                hit = True
                break
        if hit:
            self.logger.log("Write Hit " + str(hex(address)))
        else:
            self.logger.log("Write Miss " + str(hex(cache_line)))
            self.accesses.insert(0,cache_line)
            if len(self.accesses) > self.max_size:
                address = self.accesses.pop()
                self.lower_store(address << int(math.log(self.line_size) / math.log(2)))
                             
    def complete_load(self, address):
        cache_line = self.get_cache_line(address)

        if self.load_mshr_bank.isInMSHR(cache_line):
            self.load_mshr_bank.clear(cache_line)

            for line in self.accesses:
                if line == cache_line:
                    self.accesses.remove(cache_line)
                    break

            self.accesses.insert(0, cache_line)

            if len(self.accesses) > self.max_size:
                address = self.accesses.pop()
                self.lower_store(address << int(math.log(self.line_size) / math.log(2)))
                
        self.load_queue.append([address, self.latency])

        while self.load_mshr_bank.isMSHRAvailable() and len(self.load_stall_queue) > 0:
            self.load(self.load_stall_queue.pop(0))

    def advance_load(self, cycles):
        self.logger.log(self.load_queue)
        remove_list = []
        
        for i in range(len(self.load_queue)):
            self.load_queue[i][1] -= cycles

            if self.load_queue[i][1] <= 0:
                self.logger.log("Handing over to " + self.sys.hierarchy[self.sys_component_id-1].name + ".")

                cache_line = self.load_queue[i][0] >> int(math.log(self.line_size) / math.log(2))
                self.return_load(self.load_queue[i][0])
                    
                remove_list.append(i)
                
        remove_list.reverse()
        for i in remove_list:
            self.load_queue.pop(i)
        
    def advance_store(self, cycles):
        remove_list = []
        for i in range(len(self.store_queue)):
            self.store_queue[i][1] -= cycles

            if self.store_queue[i][1] <= 0:
                address = int(self.store_queue[i][0])
                remove_list.append(i)
                self.complete_store(address)

        remove_list.reverse()
        for i in remove_list:
            self.store_queue.pop(i)

        remove_list = []
        i = 0
        for addr in self.store_stall_queue:
            if len(self.store_queue) < self.num_parallel_stores:
                self.store_queue.append([addr, self.latency])
                remove_list.append(i)
            i += 1

        remove_list.reverse()
        for i in remove_list:
            self.store_stall_queue.pop(i)
            
    def advance(self, cycles):
        self.clk += cycles

        self.advance_load(cycles)
        self.advance_store(cycles)
        
        if len(self.load_queue) == 0 and \
           len(self.load_stall_queue) == 0 and \
           len(self.store_queue) == 0 and \
           len(self.store_stall_queue) == 0:
            self.is_idle = True

    def flush(self):
        self.logger.log("Flush")
        for access in self.accesses:
            self.lower_store(access)
