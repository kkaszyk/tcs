import sys

class MemSys():
    def __init__(self, name, cache_line_size):
        self.name = name
        self.hierarchy = []
        self.__cache_line_size = cache_line_size
        self.mem_trace = {}
        self.component_map = {}
        self.clock = 0
        
    def build_map(self):
        smallest_tick = sys.maxsize
        for component in self.hierarchy:
            smallest_tick = min(smallest_tick, component.clk_speed)
            higher = component.get_component_id()
            lower = component.get_lower_component_id()
            if lower != None and higher != None:
                if lower in self.component_map.keys():
                    self.component_map[lower].append(higher)
                else:
                    self.component_map[lower] = [higher]

        self.smallest_tick = smallest_tick
        
        for component in self.hierarchy:
            component.set_unit_tick(smallest_tick)
            
    def insert_pair_into_mem_trace(self, target_id, source_id, address):
        if target_id in self.mem_trace.keys():
            self.mem_trace[target_id].append((source_id,address))
        else:
            self.mem_trace[target_id] = [(source_id, address)]
        
    def retrieve_target_from_mem_trace(self, source_id, address):
        ret = -1
        if source_id in self.mem_trace.keys():
            for (target_id, addr) in self.mem_trace[source_id]:
                if address == addr:
                    ret = target_id
                    break
                
        assert ret != -1, "No target found when retrieving pair from mem_trace"
        return ret
            
    def append(self, component):
        self.hierarchy.append(component)
        return len(self.hierarchy) - 1
        
    def set_hierarchy(self, hierarchy):
        self.hierarchy = hierarchy

    def advance(self, ticks):
        self.clock += 1
        for unit in self.hierarchy:
            unit.advance(unit.unit_tick)

    def lower_load(self, address, source_id):
        target_id = self.hierarchy[source_id].get_lower_component_id()
        self.insert_pair_into_mem_trace(target_id, source_id, address)
        self.hierarchy[target_id].load(address)

    def return_load(self, address, source_id):
        for lower_id in self.component_map[source_id]:
            print("Sending from " + self.hierarchy[source_id].name + " to " + self.hierarchy[lower_id].name)
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

        print(str(max_time) + " seconds elapsed")

class MemSysComponent():
    def __init__(self, name, clk_speed, mem_sys, lower_component):
        self.name = name
        self.mem_sys = mem_sys
        self.mem_sys_component_id = mem_sys.append(self)
        self.mem_sys_lower_component_id = lower_component
        self.clk_speed = clk_speed
        self.clk = 0

    def set_unit_tick(self, smallest_clk):
        self.unit_tick = self.clk_speed / smallest_clk
        print("Unit tick: " + str(self.unit_tick))
        
    def get_component_id(self):
        return self.mem_sys_component_id

    def get_lower_component_id(self):
        return self.mem_sys_lower_component_id

    def lower_load(self, address):
        self.mem_sys.lower_load(address, self.mem_sys_component_id)

    def return_load(self, address):
        self.mem_sys.return_load(address, self.mem_sys_component_id)
