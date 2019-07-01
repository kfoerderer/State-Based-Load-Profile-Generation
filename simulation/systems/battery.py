"""

Provides a battery simulator

"""

import math
from . import actions
from . import system
#from .actions import *
#from .system import *

class Battery(system.AbstractSystem):
    
    def __init__(self, capacity, max_power, granularity, initial_charge, charging_efficiency, discharging_efficiency, relative_loss, absolute_loss):
        """
        Constructor
        Parameters:
            capacity: storage capacity in kWh
            max_power: maximum power in + and - direction
            granularity: 2 * granularity + 1 actions will be created within (-maximum power, +maximum power)
            initial_charge: initial charge in kWh
            charging_efficiency: efficiency of charging
            discharging_efficiency: efficiency of discharging
            relative_loss: relative loss of charge per tick
            absolute_loss: absolute loss of charge per tick in Ws
        """
        super().__init__()
        
        # build action set
        # determine number of decimals needed
        decimals = max(0, math.ceil(math.log(granularity,10) - math.log(max_power,10)))
        
        self.add_action(actions.Action(granularity, 0))
        for i in range(0, granularity):
            self.add_action(actions.Action(i, round(max_power * (i / granularity - 1), decimals)))
            self.add_action(actions.Action(granularity + 1 + i, round(max_power * ((i+1) / granularity), decimals)))
        
        self.capacity = capacity * 1000 * 60 * 60 # Ws
        
        self.charging_efficiency = charging_efficiency
        self.discharging_efficiency = discharging_efficiency
        self.relative_loss_per_tick = relative_loss
        self.absolute_loss_per_tick = absolute_loss
        
        self.set_state(initial_charge)
        
        
    def get_feasible_action_idxs(self, delta_time):
        # determine feasible actions
        feasible_action_idxs = []
        # determine max and min power
        
        # No losses on losses
        # c(t+1) = [c(t) (1 - l_r/2) + delta_c(t) - l_a] / [1 + l_r/2]
        # delta_c(t) = c(t+1) (1 + l_r/2) - c(t) (1 - l_r/2) + l_a
        max_power = (self.capacity * (1 + self.relative_loss_per_tick/2) - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
        max_power = max_power / self.charging_efficiency / delta_time # Ws / s
        min_power = (0 - self.charge * (1 - self.relative_loss_per_tick/2)  + self.absolute_loss_per_tick)
        min_power = min_power * self.discharging_efficiency / delta_time # Ws / s
        
        # iteratre all actions
        for idx in range(0,len(self.actions)):
            # is it feasible?
            if self.actions[idx].el_power * 1000 <= max_power and self.actions[idx].el_power * 1000 >= min_power:
                feasible_action_idxs.append(idx)
                
        return feasible_action_idxs
    
    
    def set_state(self, charge):
        """
        Sets the current charge of the battery given in kWh.        
        """
        self.charge = charge * 1000 * 60 * 60 # Ws
        
                
    def get_state_of_charge(self):
        """
        Return: current state of charge [%].
        """
        return self.charge / self.capacity    
    
    
    def state_transition(self, delta_time, action_idx, environment_interaction=None):
        """ 
        Executes a simulation step.  
        
        Return: returns an object of type SystemEnvironmentInteraction, specifying the interaction during the past state transition.  
        """
        # has an action been specified?
        if action_idx is None:
            power = 0 # idling always works out
        else:
            power = self.actions[action_idx].el_power * 1000

        delta_c = 0
        if power > 0:
            # charging
            delta_c = power * delta_time * self.charging_efficiency 
        elif power < 0:
            # discharging
            delta_c = power * delta_time / self.discharging_efficiency

        self.charge = (delta_c + self.charge * (1 - self.relative_loss_per_tick / 2) - self.absolute_loss_per_tick) / (1 + self.relative_loss_per_tick / 2)
        
        return system.SystemEnvironmentInteraction(self.actions[action_idx].el_power, self.actions[action_idx].th_power)