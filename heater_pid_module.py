from math import sqrt
from simple_pid import PID

from constants import heater_resistance, heater_max_power


class HeaterPID:
    def __init__(self, heater_PSU, target_temperature, sample_time):
        self.heater_PSU = heater_PSU
        self.heater_max_current = sqrt(heater_max_power / heater_resistance)
        self.heater_max_voltage = sqrt(heater_max_power * heater_resistance)

        self.heater_PSU.setvoltage(0)
        self.heater_PSU.setcurrent(self.heater_max_current)
        self.heater_PSU.enableoutput(True)

        self.pid = PID(Kp=15.7, Ki=0.058, Kd=0.0, setpoint=target_temperature, auto_mode=False)
        self.pid_max_output = min(self.heater_max_voltage, self.heater_PSU.VMAX * 0.9)
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
