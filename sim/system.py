 
import sys
from component import Component

class Sys():
    def __init__(self, name, cache_line_size):
        self.name = name
        self.hierarchy = []
        self.__cache_line_size = cache_line_size
        self.mem_trace = {}
        self.clock = 0
        self.eos = False

    def print_hierarchy(self):
        print("HIERARCHY:")
        for c in self.hierarchy:
            print(c.name)
            if c.parent_component != None:
                for p in c.get_parent_component_id():
                    print("   " + str(self.hierarchy[p].name))
        print("==========")
        
    def build_map(self):
        largest_tick = 0
        for component in self.hierarchy:
            largest_tick = max(largest_tick, component.clk_speed)

        self.largest_tick = largest_tick
        
        for component in self.hierarchy:
            component.set_unit_tick(largest_tick)
            
    def append(self, component):
        self.hierarchy.append(component)
        return len(self.hierarchy) - 1

    def get_idle_count(self):
        idle_count = 0
        for unit in self.hierarchy:
            if unit.is_idle:
                idle_count +=1

        return idle_count
        
    def advance(self, ticks):
        self.clock += 1

        for unit in self.hierarchy:
            unit.advance(unit.unit_tick)
        
        if self.get_idle_count() == len(self.hierarchy) and self.eos:
            self.prepare_end_sim()

    def stall(self, sched_item):
        pass
    
    def complete_sim(self):
        self.printclks()
        print("Finishing Simulation")
        sys.exit()
        
    def prepare_end_sim(self):
        self.ending = True
        self.eos = False
        
        for e in self.hierarchy:
            e.flush()

        while self.get_idle_count() != len(self.hierarchy):
            self.advance(1)

        self.complete_sim()
            
    def lower_load(self, address, source_id):
        target_id = self.hierarchy[source_id].get_child_component_id()[0]
        self.hierarchy[target_id].load(address)

    def lower_store(self, address, source_id):
        target_id = self.hierarchy[source_id].get_child_component_id()[0]
        self.hierarchy[target_id].store(address)

    def return_load(self, address, source_id):
        for lower_id in self.hierarchy[source_id].get_parent_component_id():
            self.hierarchy[lower_id].complete_load(address)

    def get_cache_line_size(self):
        return self.__cache_line_size

    def printclks(self):
        print("============")
        print("Clocks:")
        max_time = 0
        for component in self.hierarchy:
            print(component.name + ": " + str(int(component.clk)))
            if max_time < component.clk / component.clk_speed:
                max_time = component.clk / component.clk_speed

        print(str(round(max_time * 1e9)) + " ns elapsed")

    def end_sim(self):
        self.eos = True
