

class TestPSU:
    name = "Test psu"

    def __init__(self, port,):
        super().__init__()

        self.VMIN = 0
        self.VMAX = 100
        self.IMAX = 10
        self.VRESSET = 1
        self.VRESSETCNT = 0 #len(str(self.VRESSET).split(".")[1])
        self.IRESSET = 1
        self.IRESSETCNT = 0 #len(str(self.IRESSET).split(".")[1])
        self.PMAX = 300
        self.port = port
        self.name = "Test PSU"
        self.MODEL = "Test"
        self.voltage = 0
        self.current = 0
        self.polarity = True

    def turnoff(self):
        pass

    def turnon(self):
        pass

    def setvoltage(self, voltagetarget):
        self.voltage = voltagetarget
        #self.current = self.voltage * 0.1
        #print("Setvoltage : ", self.port, voltagetarget)

    def setcurrent(self, current):
        self.current = current
        # print("Setcurrent : ", current)

    def read(self, n=0, vgs=1):
        self.current = (self.voltage * 0.5) ** vgs
        if self.current > self.IMAXwidget.widgetSpinbox.value():
            return {"voltage": self.voltage, "current": self.IMAXwidget.widgetSpinbox.value(), "mode": "CC"}
        return {"voltage": self.voltage, "current": self.current, "mode": "CV"}