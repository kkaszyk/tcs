import math
from util import Logger
from mem_sys import MemSysComponent

class Memory(MemSysComponent):
    def __init__(self, sys, latency, logger_on):
        super().__init__("Memory", sys)
        self.mem_queue = []
        self.latency = latency
        self.logger = Logger("Memory", logger_on)
        
    def load(self, address):
        self.logger.log("Load " + str(address))
        self.mem_queue.append([address, self.latency])

    def advance(self, cycles):
        self.logger.log(self.mem_queue)

        remove_list = []
        address_list = []
        
        for i in range(len(self.mem_queue)):
            self.mem_queue[i][1] = self.mem_queue[i][1] - cycles
            if self.mem_queue[i][1] == 0:
                self.return_load(self.mem_queue[i][0])
                remove_list.append(i)
        
        for i in remove_list:
            self.mem_queue.pop(i)

        return address_list
