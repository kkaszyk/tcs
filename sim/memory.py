import math
from util import Logger
from mem_sys import MemSysComponent

class Memory(MemSysComponent):
    def __init__(self, sys, latency, max_parallel_loads, max_parallel_stores, tfrs_per_clk, bit_width, clk_speed, logger_on, lower_component_id):
        super().__init__("Memory", clk_speed, sys, lower_component_id)
        self.load_mem_queue = []
        self.store_mem_queue = []
        self.latency = latency
        self.logger = Logger(self.name, logger_on, self.mem_sys)

        self.max_parallel_loads = max_parallel_loads
        self.max_parallel_stores = max_parallel_stores
        self.tfrs_per_clk = tfrs_per_clk
        self.bit_width = bit_width
        self.clk_speed = clk_speed #MHz
        self.clk = 0

    def print_bandwidth(self):
        bandwidth = self.clk_speed * self.tfrs_per_clk * self.bit_width
        print(str(bandwidth) + " Mbits/s")
        print(str(bandwidth/self.bit_width) + " MT/s")
        print(str(bandwidth/8/1000) + " GB/s")
        
    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
        self.load_mem_queue.append([address, self.latency])
        self.is_idle = False

    def store(self, address):
        self.logger.log("Store " + str(hex(address)))
        self.store_mem_queue.append([address, self.latency])
        self.is_idle = False

    def advance_load(self, cycles):
        self.logger.log("Load " + str(self.load_mem_queue))

        remove_list = []

        for i in range(self.max_parallel_loads):
            if i < len(self.load_mem_queue):
                self.load_mem_queue[i][1] = self.load_mem_queue[i][1] - cycles
                if self.load_mem_queue[i][1] <= 0:
                    self.return_load(self.load_mem_queue[i][0])
                    remove_list.append(i)

        remove_list.reverse()
        for i in remove_list:
            self.load_mem_queue.pop(i)
            
    def advance_store(self, cycles):
        self.logger.log("Store " + str(self.store_mem_queue))

        remove_list = []

        for i in range(self.max_parallel_stores):
            if i < len(self.store_mem_queue):
                self.store_mem_queue[i][1] = self.store_mem_queue[i][1] - cycles
                if self.store_mem_queue[i][1] <= 0:
                    self.logger.log("Store " + str(self.store_mem_queue[i][0]) + " completed")
                    remove_list.append(i)

        remove_list.reverse()
        for i in remove_list:
            self.store_mem_queue.pop(i)
        
    def advance(self, cycles):
        self.clk += cycles

        self.advance_load(cycles)
        self.advance_store(cycles)
        
        if len(self.load_mem_queue) == 0 and len(self.store_mem_queue) == 0:
            self.is_idle = True
