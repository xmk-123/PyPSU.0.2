from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
from constants import temperature_allowance


class TemperatureWorker(QObject):

    temperature_data = pyqtSignal(float)
    finished = pyqtSignal()
    temp_stable = pyqtSignal(bool)

    def __init__(self, sensor):
        super().__init__()
        self.sensor = sensor
        self.poller = QTimer(self)
        self.match = 0
        self.refreshtime = 1000  # ms
        self.temperature_stable = False

    @pyqtSlot()
    def start_temp_controller(self):
        if self.sensor is None:
            self.temp_stable.emit(True)
            self.temperature_data.emit(0)
        else:
            self.temperature_stable = False
            self.temp_stable.emit(False)
            self.temperature_last = self.sensor.get_temperature()

            self.poller.timeout.connect(self.read_sensor)
            self.poller.start(self.refreshtime)

        if self.thread().isInterruptionRequested():
            print("isInterruptionRequested")
            self.end_temperaturemonitor()
            return

    def read_sensor(self):
        if self.thread().isInterruptionRequested():
            self.end_temperaturemonitor()
            return
        temperature = self.sensor.get_temperature()
        self.temperature_data.emit(temperature)
        print("isInterruptionRequested222")
        if self.sensor is not None:
            if self.temperature_last - temperature_allowance <= temperature <= self.temperature_last + temperature_allowance:
                self.match += 1
                if self.match == 1:
                    self.set_temperature_drift_status(True)
            else:
                self.match = 0
                self.set_temperature_drift_status(False)
                self.temperature_last = temperature
        else:
            self.set_temperature_drift_status(True)

    def set_temperature_drift_status(self, status):
        if status is not self.temperature_stable:
            self.temperature_stable = status
            self.temp_stable.emit(status)

    @pyqtSlot()
    def end_temperaturemonitor(self):
        print("in end_temperaturemonitor method of temperaturemonitor")
        if self.sensor is not None:
            self.poller.stop()
            print("poller stopped from temperaturemonitor // poller active = " + str(self.poller.isActive()))
            # self.poller = None
        self.finished.emit()

