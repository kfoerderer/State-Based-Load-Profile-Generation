"""

Provides a battery simulator

"""

import math
from . import actions
from . import system
#from .actions import *
#from .system import *

class CHPPlant(system.AbstractSystem):
    
    def __init__(self, actions, initial_mode, initial_staying_time, el_ramp_up_rate, el_ramp_down_rate, th_ramp_up_rate, th_ramp_down_rate):
        """
        Constructor
        Parameters:
            actions: dictionary of the following form
                {idx: action} with actions {idx, el_power, th_power, min_staying_time, max_staying_time, *}
            initial_mode: idx of initial mode
            initial_staying_time: elapsed staying time in initial mode in seconds
            ramp_up_rate: ramping rate (>0) for ramp up in kW/s
            ramp_down_rate: ramping rate (>0) for ramp down in kW/s 
        """
        super().__init__()
        
        # set actions
        self.actions = actions
        
        # state data
        self.mode = initial_mode
        self.staying_time = initial_staying_time
        self.el_power = self.actions[self.mode].el_power
        self.th_power = self.actions[self.mode].th_power
        
        # set ramping parameters
        self.el_ramp_up_rate = -el_ramp_up_rate
        self.el_ramp_down_rate = el_ramp_down_rate
        self.th_ramp_up_rate = -th_ramp_up_rate
        self.th_ramp_down_rate = th_ramp_down_rate
    
    
    def set_state(self, mode, staying_time):
        if not isinstance(mode, int):
            raise ValueError("Mode must be an integer")
        self.mode = mode
        self.staying_time = staying_time
        self.el_power = self.actions[mode].el_power
        self.th_power = self.actions[mode].th_power
    
    
    def get_feasible_action_idxs(self, delta_time):
        # determine feasible actions
        feasible_action_idxs = []
        
        if self.actions[self.mode].min_staying_time > self.staying_time: # has the current mode been active long enough?
            feasible_action_idxs.append(self.mode) # no, stay in mode
        else: # yes it has
            for idx in self.actions:
                if idx == self.mode and self.staying_time + delta_time <= self.actions[idx].max_staying_time : 
                    feasible_action_idxs.append(idx) # current mode & time limit not yet reached
                else: 
                    feasible_action_idxs.append(idx) # different mode -> feasible
                    
        return feasible_action_idxs
    
    
    def state_transition(self, delta_time, action_idx, environment_interaction=None):
        """                
        Executes a simulation step.  
        
        Return: returns an object of type SystemEnvironmentInteraction, specifying the interaction during the past state transition.
        """        
        
        sys_env_interaction = system.SystemEnvironmentInteraction()
        
        # update mode if it changed
        if action_idx != self.mode:
            self.mode = action_idx
            self.staying_time = 0         
        
        # do ramping if necessary
                
        # electrical
        total_energy = 0
        initial_power = self.el_power            
        remaining_ramping_power = self.actions[self.mode].el_power - self.el_power # kW
        if remaining_ramping_power < 0:
            # ramp up
            remaining_ramping_time = remaining_ramping_power / self.el_ramp_up_rate # seconds
            self.el_power = max(self.actions[self.mode].el_power, initial_power + self.el_ramp_up_rate * delta_time) # for float comparison
            total_energy = (min(delta_time, remaining_ramping_time) * (initial_power + self.el_power) / 2 + # ramp up
                            max(0, delta_time - remaining_ramping_time) * self.el_power) # ramping finished
        elif remaining_ramping_power > 0:
            # ramp down
            remaining_ramping_time = remaining_ramping_power / self.el_ramp_down_rate # seconds
            self.el_power = min(self.actions[self.mode].el_power, initial_power + self.el_ramp_down_rate * delta_time) # for float comparison
            total_energy = (min(delta_time, remaining_ramping_time) * (initial_power + self.el_power) / 2 + # ramp up
                            max(0, delta_time - remaining_ramping_time) * self.el_power) # ramping finished
        total_energy = delta_time * self.el_power    
        # compute average power
        sys_env_interaction.el_power = total_energy / delta_time
            
        # thermal
        total_energy = 0
        initial_power = self.th_power      
        remaining_ramping_power = self.actions[self.mode].th_power - self.th_power # kW
        if remaining_ramping_power < 0:
            # ramp up
            remaining_ramping_time = remaining_ramping_power / self.th_ramp_up_rate # seconds
            self.th_power = max(self.actions[self.mode].th_power, initial_power + self.th_ramp_up_rate * delta_time) # for float comparison
            total_energy = (min(delta_time, remaining_ramping_time) * (initial_power + self.th_power) / 2 + # ramp up
                            max(0, delta_time - remaining_ramping_time) * self.th_power) # ramping finished
        elif remaining_ramping_power > 0:
            # ramp down
            remaining_ramping_time = remaining_ramping_power / self.th_ramp_down_rate # seconds
            self.th_power = min(self.actions[self.mode].th_power, initial_power + self.th_ramp_down_rate * delta_time) # for float comparison
            total_energy = (min(delta_time, remaining_ramping_time) * (initial_power + self.th_power) / 2 + # ramp up
                            max(0, delta_time - remaining_ramping_time) * self.th_power) # ramping finished
        else:
            total_energy = delta_time * self.th_power
                
        # compute average power
        sys_env_interaction.th_power = total_energy / delta_time            
            
        self.staying_time += delta_time      
            
        return sys_env_interaction
        
        
    