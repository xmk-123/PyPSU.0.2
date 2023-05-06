from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot, QSettings
# from constants import temperature_allowance, temperature_matches_for_stable, shutdown_temperature, heater_resistance, heater_max_power
from math import sqrt

from PyQt5.QtWidgets import QMessageBox
from simple_pid import PID


class TemperatureWorker(QObject):

    temperature_data = pyqtSignal(float)
    finished = pyqtSignal()
    temp_stable = pyqtSignal(bool)
    overheat = pyqtSignal()

    def __init__(self, _psudict, target_temperature):
        super().__init__()
        self.saved_parameters = QSettings()
        self.update_parameters()
        self.sensor = _psudict["Temperature Sensor"]
        self.poller = QTimer(self)
        self.match = 0
        self.refreshtime = 1000  # ms
        self.temperature_stable = False
        self.target_temperature = target_temperature
        self.temperature_last = self.sensor.get_temperature()

        if _psudict["Heater PSU"].name != "Empty PSU":
            self.heater_pid = HeaterPID(_psudict["Heater PSU"], target_temperature, self.refreshtime / 1000, self.heater_resistance, self.heater_max_power)
            self.heater_present = True
        else:
            self.heater_present = False

    def update_parameters(self):
        self.heater_resistance = int(self.saved_parameters.value("heater_resistance"))
        self.heater_max_power = int(self.saved_parameters.value("heater_max_power"))
        self.shutdown_temperature = int(self.saved_parameters.value("shutdown_temperature"))
        self.temperature_allowance = float(self.saved_parameters.value("temperature_allowance"))
        self.temperature_matches_for_stable = int(self.saved_parameters.value("temperature_matches_for_stable"))

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
        if temperature >= self.shutdown_temperature:
            if self.heater_present:
                self.heater_pid.turn_off()
            self.overheat.emit()
            self.end_temperature_controller()

        self.temperature_data.emit(temperature)

        if self.heater_present:
            self.heater_pid.sensor_temp(temperature)
            if self.target_temperature - self.temperature_allowance <= temperature <= \
                    self.target_temperature + self.temperature_allowance:
                self.match += 1
                if self.match == self.temperature_matches_for_stable:
                    self.set_temperature_drift_status(True)
            else:
                self.match = 0
                self.set_temperature_drift_status(False)
        else:
            if self.temperature_last - self.temperature_allowance <= temperature <= \
                    self.temperature_last + self.temperature_allowance:
                self.match += 1
                if self.match == self.temperature_matches_for_stable:
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
        if self.heater_present:
            self.heater_pid.turn_off()
        self.finished.emit()


class HeaterPID:
    def __init__(self, heater_PSU, target_temperature, sample_time, heater_resistance, heater_max_power):
        self.heater_PSU = heater_PSU
        self.heater_max_current = sqrt(heater_max_power / heater_resistance)
        self.heater_max_voltage = sqrt(heater_max_power * heater_resistance)

        self.heater_PSU.setvoltage(0)
        self.heater_PSU.setcurrent(self.heater_max_current)
        self.heater_PSU.enableoutput(True)

        self.pid = PID(Kp=15.7, Ki=0.058, Kd=0.0, setpoint=target_temperature, auto_mode=False)
        self.pid_max_output = min(self.heater_max_voltage, self.heater_PSU.VMAX)
        self.pid.output_limits = (0, self.pid_max_output)
        self.pid.sample_time = sample_time  # seconds

        self.last_temperature_reading = 0
        self.last_heater_voltage = 0

        self.pid.set_auto_mode(True)

    def sensor_temp(self, temperature):
        _heater_voltage = self.pid(temperature)
        if self.last_heater_voltage != _heater_voltage:
            self.heater_PSU.setvoltage(_heater_voltage)
            self.last_heater_voltage = _heater_voltage

    def turn_off(self):
        self.heater_PSU.setvoltage(0)
        self.heater_PSU.setcurrent(0)
        self.heater_PSU.enableoutput(False)

    def pid_set_last_output(self, voltage):
        print("setting pid last = " + str(voltage))
        self.pid.set_auto_mode(False)
        # self.pid.reset()
        self.pid.set_auto_mode(True, last_output=self.last_heater_voltage + voltage)
        self.last_heater_voltage += voltage


