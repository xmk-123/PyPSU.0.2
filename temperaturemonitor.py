
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
        self.refreshtime = 1000  # ms
        self.temperature_stable = False

        try:
            self.sensor = TemperatureSensor(UART_Adapter('/dev/ttyUSB'))
        except(DeviceError, AdapterError) as e:
            print(e)
            self.sensor = None

    @pyqtSlot()
    def start_temp_controller(self):
        if self.sensor is None:
            self.temp_stable.emit(True)
            self.temperature_data.emit(0)
        else:
            self.temperature_last = self.sensor.get_temperature()
            self.poller = QTimer(self)
            self.poller.timeout.connect(self.read_sensor)
            self.poller.start(self.refreshtime)

    def read_sensor(self):
        temperature = self.sensor.get_temperature()
        self.temperature_data.emit(temperature)
        if self.sensor.name != "Dummy":
            if self.temperature_last - temperature_allowance <= temperature <= self.temperature_last + temperature_allowance:
                self.match += 1
                if self.match == 5:
                    self.set_temperature_drift_status(True)
                else:
                    self.match = 0
                    self.set_temperature_drift_status(False)
        else:
            self.set_temperature_drift_status(True)

    def set_temperature_drift_status(self, status):
        if status is not self.temperature_stable:
            self.temperature_stable = status
            self.temp_stable.emit(status)

    @pyqtSlot()
    def end_temperaturemonitor(self):
        if self.sensor is not None:
            self.poller.stop()
        self.finished.emit()
