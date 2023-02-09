from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot
from constants import temperature_allowance, temperature_matches_for_stable, shutdown_temperature

from heater_pid_module import HeaterPID


class TemperatureWorker(QObject):

    temperature_data = pyqtSignal(float)
    finished = pyqtSignal()
    temp_stable = pyqtSignal(bool)

    def __init__(self, _psudict, target_temperature):
        super().__init__()
        self.sensor = _psudict["Temperature Sensor"]
        self.poller = QTimer(self)
        self.match = 0
        self.refreshtime = 1000  # ms
        self.temperature_stable = False
        self.target_temperature = target_temperature
        self.temperature_last = self.sensor.get_temperature()

        if _psudict["Heater PSU"].name != "Empty PSU":
            self.heater_pid = HeaterPID(_psudict["Heater PSU"], target_temperature, self.refreshtime / 1000)
            self.heater_present = True
        else:
            self.heater_present = False

    def start_temp_controller(self):
        self.temperature_stable = False
        self.temp_stable.emit(False)

        self.poller.timeout.connect(self.read_sensor)
        self.poller.start(self.refreshtime)

        if self.thread().isInterruptionRequested():
            self.end_temperature_controller()
            return

    def read_sensor(self):

        if self.thread().isInterruptionRequested():
            self.end_temperature_controller()
            return

        temperature = self.sensor.get_temperature()
        if temperature >= shutdown_temperature:
            self.heater_pid.turn_off()

        self.temperature_data.emit(temperature)

        if self.heater_present:
            self.heater_pid.sensor_temp(temperature)
            if self.target_temperature - temperature_allowance <= temperature <= \
                    self.target_temperature + temperature_allowance:
                self.match += 1
                if self.match == temperature_matches_for_stable:
                    self.set_temperature_drift_status(True)
            else:
                self.match = 0
                self.set_temperature_drift_status(False)
        else:
            if self.temperature_last - temperature_allowance <= temperature <= \
                    self.temperature_last + temperature_allowance:
                self.match += 1
                if self.match == temperature_matches_for_stable:
                    self.set_temperature_drift_status(True)
            else:
                self.match = 0
                self.set_temperature_drift_status(False)
                self.temperature_last = temperature

    def set_temperature_drift_status(self, status):
        if status is not self.temperature_stable:
            self.temperature_stable = status
            self.temp_stable.emit(status)

    def update_pid(self, voltage):
        print("Updating pid last V : " + str(voltage))
        self.poller.stop()
        self.heater_pid.pid_set_last_output(voltage)
        self.poller.start(self.refreshtime)

    def end_temperature_controller(self):
        self.poller.stop()
        print("poller stopped from temperaturemonitor // poller active = " + str(self.poller.isActive()))
        if self.heater_present:
            self.heater_pid.turn_off()
        self.finished.emit()


