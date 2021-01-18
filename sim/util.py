class Logger():
    def __init__(self, name, on, sys):
        self.on = on
        self.name = name
        self.sys = sys
        
    def log(self, string):
        if self.on:
            print(str(self.sys.clock) + ": " + self.name + ": " + str(string))
