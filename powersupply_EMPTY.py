

class EmptyPSU:
    name = "Empty psu"

    def __init__(self, port=None):
        super().__init__()
        self.VMIN = 0
        self.VMAX = 1
        self.IMAX = 1
        self.VRESSET = 1
        self.VRESSETCNT = 1
        self.IRESSET = 1
        self.IRESSETCNT = 1
        self.PMAX = 1
        self.port = "None"
        self.name = "Empty PSU"
        self.MODEL = "Empty"

    def setvoltage(self, x=None):
        pass

    def setcurrent(self, x=None):
        pass

    def output(self, enable: bool):
        pass
