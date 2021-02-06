class Component():
    def __init__(self, name, clk_speed, sys, parent_component_id, child_component_id):
        self.name = name
        self.sys = sys
        self.sys_component_id = sys.append(self)
        self.clk_speed = clk_speed
        self.clk = 0
        self.is_idle = True
        self.parent_component = parent_component_id
        self.child_component = child_component_id
        #self.clock = 0

    def reset(self):
        self.clk = 0
        self.is_idle = True
        
    def set_child_component(self, child_component):
        self.child_component = child_component

    def set_parent_component(self, parent_component):
        self.parent_component = parent_component

    def append_parent_component(self, parent_component):
        if self.parent_component == None:
            self.parent_component = [parent_component]
        else:
            self.parent_component.append(parent_component)
    
    def is_idle(self):
        return self.is_idle

    def set_unit_tick(self, largest_clk):
        self.unit_tick = self.clk_speed / largest_clk

    def get_component_id(self):
        return self.sys_component_id

    def get_parent_component_id(self):
        return self.parent_component
    
    def get_child_component_id(self):
        return self.child_component
    
    def flush(self):
        pass

    def advance(self, cycles):
        #self.clock += cycles
        self.clk += cycles

class SchedComponent(Component):
    def __init__(self, name, clk_speed, sys, parent_component_id, child_component_id):
        super().__init__(name, clk_speed, sys, parent_component_id, child_component_id)

    def schedule(self):
        pass

class MemSysComponent(Component):
    def __init__(self, name, clk_speed, sys, parent_component_id, child_component_id):
        super().__init__(name, clk_speed, sys, parent_component_id, child_component_id)

    def lower_load(self, address):
        self.sys.lower_load(address, self.sys_component_id)

    def lower_store(self, address):
        self.sys.lower_store(address, self.sys_component_id)

    def return_load(self, address):
        self.sys.return_load(address, self.sys_component_id)
