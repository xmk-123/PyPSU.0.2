

class EmptyPSU:
    name = "Empty psu"

    def __init__(self, port):
        super().__init__()
        self.VMIN = 0
        self.VMAX = 0
        self.IMAX = 0
        self.VRESSET = 1
        self.VRESSETCNT = 1
        self.IRESSET = 1
        self.IRESSETCNT = 1
        self.port = "None"
        self.name = "Empty PSU"
        self.MODEL = "Empty"
