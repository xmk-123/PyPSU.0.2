import powersupply_EMPTY
import powersupply_TEST
from powersupply_KORAD import KORAD
from powersupply_TEST import TestPSU
from powersupply_EMPTY import EmptyPSU

physicalpsusClasses = {"Korad": KORAD,
                       "Test PSU": TestPSU,
                       "Empty PSU": EmptyPSU}
temperature_allowance = 1
