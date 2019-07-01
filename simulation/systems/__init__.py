"""

Module comprising simulation models of energy systems.

"""

from systems.actions import *
from systems.system import *
from systems.battery import *
from systems.combined_heat_and_power_plant import *
from systems.heat_storage import *

# Constants
KWH_PER_KJ = 0.000277778 # kWh / kJ

WATER_DENSITY = 1000 # kg/m^3
WATER_HEAT_CAPACITY = 4.190 * KWH_PER_KJ # kJ / (kg K) * kWh / kJ
