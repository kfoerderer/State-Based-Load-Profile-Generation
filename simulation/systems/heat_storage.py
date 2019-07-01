"""

Provides a battery simulator

"""

import math
from . import actions
from . import system
#from .actions import *
#from .system import *


def calculate_tank_capacity(max_temp, min_temp, volume, density, heat_capacity):
    """
    Calculates the tank capacity from the given physical quantities.
    Paramters:
        max_temp: Maximum temperature of storage in K or C
        min_temp: Minimum temperature of storage in K or C
        volume: Volume of the tank in m^3
        density: Density of the matter used in the storage kg/m^3
        heat_capacity: Heat capacity of the matter used in the storage in kWh/(kg K). Use the systems.KWH_PER_KJ constant if needed.
    """
    return ((max_temp-min_temp) * # K
            volume * density * # m^3 * kg / m^3 = kg
            heat_capacity) # kWh / (kg * K)


class HeatStorage(system.AbstractSystem):
    
    def __init__(self, capacity, initial_charge, charging_efficiency, discharging_efficiency, relative_loss, absolute_loss):
        """
        Constructor
        Parameters:
            capacity: storage capacity in kWh
            initial_charge: initial charge in kWh
            charging_efficiency: efficiency of charging
            discharging_efficiency: efficiency of discharging
            relative_loss: relative loss of charge per tick
            absolute_loss: absolute loss of charge per tick
        """
        super().__init__()
        
        self.actions = None
        
        self.capacity = capacity * 1000 * 60 * 60 # Ws
        
        self.charging_efficiency = charging_efficiency
        self.discharging_efficiency = discharging_efficiency
        self.relative_loss_per_tick = relative_loss
        self.absolute_loss_per_tick = absolute_loss
                
        self.charge = initial_charge * 1000 * 60 * 60 # Ws
        
    
    def set_state(self, charge):
        """        
        Sets the current charge of the battery given in kWh.        
        """
        self.charge = charge * 1000 * 60 * 60 # Ws
               
            
    def get_state_of_charge(self):
        """        
        Return the current state of charge [%].        
        """
        return self.charge / self.capacity    
    
    
    def state_transition(self, delta_time, action_idx, environment_interaction):
        """                
        Executes a simulation step.  
        
        Return: returns an object of type SystemEnvironmentInteraction, specifying the interaction during the past state transition.        
        """       
        # power available from other systems has negative sign -> make it positive
        energy = -environment_interaction.th_power * delta_time * 1000 # kW -> Ws
        energy_flow = 0
        diff = energy
        
        # No losses on losses
        # c(t+1) = [c(t) (1 - l_r/2) + delta_c(t) - l_a] / [1 + l_r/2]
        # delta_c(t) = c(t+1) (1 + l_r/2) - c(t) (1 - l_r/2) + l_a        
        if energy > 0:
            max_energy = (self.capacity * (1 + self.relative_loss_per_tick/2) - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
            max_energy /= self.charging_efficiency # Ws
            diff = max(0, energy-max_energy)        
            energy_flow = energy - diff
        elif energy < 0:
            min_energy = (0 - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
            min_energy *= self.discharging_efficiency # Ws 
            diff = min(0, energy-min_energy)
            energy_flow = energy - diff

        environment_interaction = system.SystemEnvironmentInteraction(environment_interaction.el_power, 0)
        # restore original sign of power
        environment_interaction.th_power = -diff / 1000 / delta_time # Ws -> kW
                         
        delta_c = 0
        if energy_flow > 0:
            # charging
            delta_c = energy_flow * self.charging_efficiency 
        elif energy_flow < 0:
            # discharging
            delta_c = energy_flow / self.discharging_efficiency

        self.charge = (delta_c + self.charge * (1 - self.relative_loss_per_tick / 2) - self.absolute_loss_per_tick) / (1 + self.relative_loss_per_tick / 2)       
        
        return environment_interaction
                 

    def filter_actions(self, function, action_map, delta_time, min_soc, max_soc):
        """
        Filter actions that would lead to exceeding boundaries
        
        Parameters:
            function: function that maps from an action to thermal power in kW            
            min_soc: minimal state of charge [0,1] allowed by the action filter
            max_soc: maximum state of charge [0,1] allowed by the action filter
        """
        # determine max and min power
        
        min_charge = self.capacity * min_soc # Ws
        max_charge = self.capacity * max_soc # Ws
        
        # No losses on losses
        # c(t+1) = [c(t) (1 - l_r/2) + delta_c(t) - l_a] / [1 + l_r/2]
        # delta_c(t) = c(t+1) (1 + l_r/2) - c(t) (1 - l_r/2) + l_a
        max_power = (self.capacity * (1 + self.relative_loss_per_tick/2) - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
        max_power = max_power / self.charging_efficiency / delta_time # Ws / s
        min_power = (0 - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
        min_power = min_power * self.discharging_efficiency / delta_time # Ws / s
        
        #print('min %d, max %d'%(min_power, max_power))
        
        filtered_actions = {}
        # iteratre all actions
        for idx in action_map:
            # is it feasible?
            thermal_power = function(action_map[idx])
            
            if self.charge < min_charge and thermal_power <= 0:
                continue
            elif self.charge == min_charge and thermal_power < 0:
                continue
                
            if self.charge >= max_charge and thermal_power > 0:
                continue
                
            if thermal_power * 1000 <= max_power and thermal_power * 1000 >= min_power:
                filtered_actions[idx] = action_map[idx]
        
        return filtered_actions