""" 
Input_VEDA Class

"""

# import statements

class InputVEDA():
    """ InputVEDA
        Object representing VEDA 
        E.g. 
    
    """
    
    # global variables here
    
    # instance initiation
    def __init__(self, crs, title, access_type, ):
        self.crs = crs
        self.title = title
        self.access_type = access_type
         
            
    def get_crs(self):
        return self.crs