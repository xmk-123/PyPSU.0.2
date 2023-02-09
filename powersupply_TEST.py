import time


class TestPSU:
    name = "Test psu"
    Vgs = 0
    Vds = 0

    def __init__(self, port):
        super().__init__()

        self.VMIN = 0
        self.VMAX = 100
        self.IMAX = 10
        self.VRESSET = 0.1
        self.VRESSETCNT = 1  # len(str(self.VRESSET).split(".")[1])
        self.IRESSET = 1
        self.IRESSETCNT = 0  # len(str(self.IRESSET).split(".")[1])
        self.PMAX = 300
        self.port = port
        self.name = "Test PSU"
        self.MODEL = "Test"
        self.voltage = 0
        self.current = 0
        self.polarity = True
        self.VOFFSETMAX = 0.1
        self.IOFFSETMAX = 0.1

        self._Serial = srl()

    def output(self, i=True):
        pass

    def setvoltage(self, voltagetarget):
        if self.port == "Test_Vgs_Port":
            TestPSU.Vgs = voltagetarget
        elif self.port == "Test_Vds_Port":
            TestPSU.Vds = voltagetarget

    def setcurrent(self, current):
        self.current = current

    def physical_psu_readings(self, n=0, vgs=1):
        time.sleep(0.1)
        if self.port == "Test_Vgs_Port":
            return {"voltage": TestPSU.Vgs, "current": 0, "mode": "CV"}
        elif self.port == "Test_Vds_Port":
            Ids = (TestPSU.Vds / 1000) + (TestPSU.Vgs * 0.1)
            if Ids > self.current:
                return {"voltage": TestPSU.Vds, "current": self.current, "mode": "CC"}
            else:
                return {"voltage": TestPSU.Vds, "current": Ids, "mode": "CV"}


class srl:
    def __init__(self):
        pass

    def close(self):
        pass
