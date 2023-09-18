""" 
Input_Reference Class

"""

# import statements

class InputReference():
    """ InputReference
        Object representing an input polygon that is compared to a VEDA object
        E.g. 
    
    """
    
    # global variables here
    
    # instance initiation
    def __init__(self, crs, title, type_, ):
        self.crs = crs
        self.title = title
        self.type_ = type_
        
            
            
    def get_crs(self):
        return self.crs