import math
from util import Logger
from mem_sys import MemSysComponent

class Memory(MemSysComponent):
    def __init__(self, sys, latency, logger_on, lower_component_id):
        super().__init__("Memory", sys, lower_component_id)
        self.mem_queue = []
        self.latency = latency
        self.logger = Logger(self.name, logger_on)
        
    def load(self, address):
        self.logger.log("Load " + str(hex(address)))
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

        print(self.mem_queue)
        remove_list.reverse()
        for i in remove_list:
            print(i)
            self.mem_queue.pop(i)

        return address_list
