"""
The class strategy will contain the different parameters
and functions associated to a strategy
"""

#===============================================================================
# LIBRARIES
#===============================================================================



#===============================================================================
# CLASS
#===============================================================================
class Strategy():
    """ 
    Class that contains all parameters and functions associated to an strategy
    """
    def __init_(self):
        self.ndowns = None
        self.nups = None
        self.pctdown = None
    
    def post_open_conditions(self, ndowns=None, pctdown=None):
        """
        It will store open conditions:
            - ndowns: Number of days with close below last close
        """
        self.ndowns = ndowns
        self.pctdown = pctdown
    
    def post_close_conditions(self, nups=None):
        """
        It will store close conditions:
            - nups: Number of days with close above last close
        """
        self.nups = nups






#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    pass