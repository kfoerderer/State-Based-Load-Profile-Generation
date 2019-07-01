"""

Base class for systems to be simulated

"""
from .actions import *

class SystemEnvironmentInteraction:
    """
    Holds data detailing the interaction between a system and its environment.
    
    Parameters:
        power_el: (average) electrict power in kW
        power_th: (average) thermal power in kW
        **kwargs: keys and values defining further attributes
    
    """
    def __init__(self, power_el=0, power_th=0, **kwargs):
        self.el_power = power_el
        self.th_power = power_th
        self.__dict__.update(kwargs)
        
    def __mul__(self, other):
        """
        Multiplication operator
        """
        self.el_power *= other
        self.th_power *= other
        
    __rmul__ = __mul__
        
    def __str__(self):
        return 'SystemEnvironmentInteraction(' + str(self.__dict__)[1:-1] + ')'
    
    
    def __repr__(self):
        return self.__str__()        



class AbstractSystem(object):
    """
    Base class for each energy system. 
    
    Sign of energy flow is as follows:
        + system consumes power
        - system releases power
        
        input (+) -> system -> output (-)
        
    
    Each "system", e.g., a battery, chp plant or an aggregate of systems, periodically performs "actions", e.g., idling, charging with a given power or discharging.
    A system implemented with this base class is able to determine all feasible actions given its current state.
    After choosing an action a state transition leads to a new state. The process looks like follows:
    
    System in current state -> derive feasible actions -> choose action to perform -> state transition -> system in new state (-> repeat)
    
    """
    
    def __init__(self):
        """
        Constructor
        Parameters: None        
        """
        self.actions = {} # dictionary: id -> Action()    
        
        
    def add_action(self, action):
        """        
        Adds an action to the actions dictionary        
        """
        if action.idx in self.actions:
            raise ValueError('Action with same index is already registered')
        self.actions[action.idx] = action
        
        
    def get_actions(self):
        """
        Returns dictionary containing all actions
        """
        return self.actions
    
    
    def get_actions_by_idxs(self, idxs):
        """
        Returns dictionary containing all actions specified by ids
        """
        return {idx: self.actions[idx] for idx in idxs}
    
    
    def get_feasible_action_idxs(self, delta_time):
        """        
        Override this!
        
        Returns a list of ids associated to feasible actions
        """
        pass
    
    
    def filter_actions(self, function, action_map, delta_time, **kwargs):
        """        
        Passive systems, i.e. system that do not act by themself, may use this method to filter actions of other systems and thereby declare them infeasible.
        
        Example: A switch that when turned off prevents any energy flow. Use action.ATTRIBUTE to identify actions to filter.        
        
        Parameters:
            function: function that maps from an action to values needed for considering the feasibility
            action_map: dictionary {idx:action} of actions to be filtered
            delta_time: time passing during next simulation step    
            **kwargs: additional parameters
        """
        return action_map # do not filter per default
    
    
    def set_state(self, **kwargs):
        """
        Function for setting a state manually
        """
        pass
    
    
    def state_transition(self, delta_time, action_idx, environment_interaction):
        """
        Override this!
        
        Executes a simulation step.  
        
        Parameters:
            delta_time: time in seconds passing during this simulation step
            action_idx: index of action to perform
            environment_interaction: the sum of all interactions the system is faced with. If this parameter is not 'None' consider it when generating the return value.
                E.g. if a storage's capacity would be exceeded when charging the energy given through this parameter, the return value should reflect the remaining amount of energy.
        
        Return: returns an object of type SystemEnvironmentInteraction, specifying the interaction during the past state transition.
        """
        return SystemEnvironmentInteraction(self.actions[action_idx].el_power, self.actions[action_idx].th_power)
    
    
    