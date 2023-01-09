
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
from digitemp.master import UART_Adapter
from digitemp.device import TemperatureSensor
from digitemp.exceptions import DeviceError, AdapterError

from constants import temperature_allowance


class TemperatureWorker(QObject):

    temperature_data = pyqtSignal(float)
    finished = pyqtSignal()
    temp_stable = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.match = 0
        self.refreshtime = 100

        try:
            self.sensor = TemperatureSensor(UART_Adapter('/dev/ttyUSB0'))
        except(DeviceError, AdapterError) as e:
            print(e)
            self.sensor = DummyTemperatureSensor()

    @pyqtSlot()
    def start_temp_controller(self):
        self.temperature_last = self.sensor.get_temperature()
        self.poller = QTimer(self)
        self.poller.timeout.connect(self.read_sensor)
        self.poller.start(self.refreshtime)

    def read_sensor(self):
        temperature = self.sensor.get_temperature()
        self.temperature_data.emit(temperature)
        print(temperature)
        if self.temperature_last - temperature_allowance <= temperature <= self.temperature_last + temperature_allowance:
            self.match += 1
            if self.match == 5:
                self.temp_stable.emit(True)
        else:
            self.match = 0
            self.temp_stable.emit(False)

    @pyqtSlot()
    def stop_poller(self):
        self.poller.stop()


class DummyTemperatureSensor:

    def get_temperature(self):
        return 99
