from powersupply_KORAD import KORAD
from powersupply_TEST import TestPSU
from powersupply_EMPTY import EmptyPSU

from digitemp.master import UART_Adapter
from digitemp.device import TemperatureSensor
from digitemp.exceptions import DeviceError, AdapterError

# to add new physical PSU or sensor
#   1)import the module
#   2)Add, into the applicable dictionary, the name as it will appear in the application's menus
#       and the class as is named in the PSU's module

physicalpsusClasses = {"Korad": KORAD,
                       "Test PSU": TestPSU,
                       "Empty PSU": EmptyPSU}

temperatureSensorsClasses = {"DS18B20": TemperatureSensor}

temperature_allowance = 0.1

temperature_matches_for_stable = 5

heater_resistance = 32
heater_max_power = 150

shutdown_temperature = 80
