"""
This module defines the Joist_and_Plank class.
"""
from .wood import Wood

class Joist_and_Plank(Wood):
    """
    Represents Joist and Plank grade lumber.

    This class is a specialization of the Wood class and is used to represent
    Joist and Plank materials. It inherits all properties and methods from the
    Wood base class.
    """
    def __init__(self, **kwargs):
        """
        Initializes the Joist_and_Plank object.

        Parameters
        ----------
        **kwargs : dict
            A dictionary of material properties, passed to the Wood constructor.
        """
        super().__init__(**kwargs)