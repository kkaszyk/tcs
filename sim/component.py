class Component():
    def __init__(self, name, clk_speed, sys, lower_component):
        self.name = name
        self.sys = sys
        self.sys_component_id = sys.append(self)
        self.clk_speed = clk_speed
        self.clk = 0
        self.is_idle = True
        self.sys_lower_component_id = lower_component
        self.clock = 0
        
    def is_idle():
        return self.is_idle

    def set_unit_tick(self, smallest_clk):
        self.unit_tick = self.clk_speed / smallest_clk

    def get_component_id(self):
        return self.sys_component_id

    def get_lower_component_id(self):
        return self.sys_lower_component_id
    
    def flush(self):
        pass

    def advance(self, cycles):
        self.clock += cycles

class SchedComponent(Component):
    def __init__(self, name, clk_speed, sys, lower_component):
        super().__init__(name, clk_speed, sys, lower_component)

    def schedule(self):
        pass
