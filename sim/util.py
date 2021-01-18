class Logger():
    def __init__(self, name, on):
        self.on = on
        self.name = name
        
    def log(self, string):
        if self.on:
            print(self.name + ": " + str(string))
