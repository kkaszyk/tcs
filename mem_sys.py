class MemSys():
    def __init__(self, name, cache_line_size):
        self.name = name
        self.hierarchy = []
        self.__cache_line_size = cache_line_size

    def append(self, component):
        self.hierarchy.append(component)
        return len(self.hierarchy) - 1
        
    def set_hierarchy(self, hierarchy):
        self.hierarchy = hierarchy

    def advance(self, cycles):
        for unit in self.hierarchy:
            unit.advance(cycles)

    def lower_load(self, address, source_id):
        self.hierarchy[source_id+1].load(address)

    def return_load(self, address, source_id):
        self.hierarchy[source_id-1].complete_load(address)

    def get_cache_line_size(self):
        return self.__cache_line_size

class MemSysComponent():
    def __init__(self, name, mem_sys):
        self.name = name
        self.mem_sys = mem_sys
        self.mem_sys_component_id = mem_sys.append(self)
        
    def lower_load(self, address):
        self.mem_sys.lower_load(address, self.mem_sys_component_id)

    def return_load(self, address):
        self.mem_sys.return_load(address, self.mem_sys_component_id)
