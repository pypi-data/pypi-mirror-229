class CustomModule:
    def __init__(self, name):
        self.name = name
    
    def hello(self):
        print("Hello {}! This is a custom module.".format(self.name))