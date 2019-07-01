"""

Action and ActionSet for action management and mapping ids to actual actions. Provides a standard way of dealing with generic actions for all simulated systems.

"""

class Action:
    """
    
    Defines a single action.
    Parameters:
        idx: index of action
        power_el: electrict power in kW
        power_th: thermal power in kW
        **kwargs: keys and values defining further attributes
    
    """
    def __init__(self, idx, el_power=0, th_power=0, **kwargs):
        self.idx = idx
        self.el_power = el_power
        self.th_power = th_power
        self.__dict__.update(kwargs)
        
        
    def __str__(self):
        return 'action(' + str(self.__dict__)[1:-1] + ')'
    
    
    def __repr__(self):
        return self.__str__()        
