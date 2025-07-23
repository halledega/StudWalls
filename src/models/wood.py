class Wood():
    def __init__(self, **kwargs):
        self._name = ""
        self._species = kwargs['Species']
        self._grade = kwargs['Grade']
        self._fb = kwargs['fb']
        self._fv = kwargs['fv']
        self._fc = kwargs['fc']
        self._fcp = kwargs['fcp']
        self._ft = kwargs['ft']
        self._E = kwargs['E']
        self._E05 = kwargs['E05']
        self._mat_type = kwargs['Type']
    
    @property
    def species(self)-> str:
        return self._species
    @species.setter
    def secies(self, value)-> None:
        self._species = value
        
    @property
    def grade(self)-> str:
        return self._grade
    @grade.setter
    def secies(self, value)-> None:
        self._grade = value
        
    @property
    def name(self)-> str:
        species_short = {
            "Douglas Fir-Larch" : "D.Fir.",
            "Hem-Fir" : "H.Fir.",
            "Spruce-Pine-Fir" : "SPF",
            "Northern Species" : "Northern"
        }
        self._name = species_short[self._species] + " " + self._grade
        return self._name

    @property
    def fb(self)-> float:
        return self._fb
    @fb.setter
    def fb(self, value)-> None:
        self._fb = value
        
    @property
    def fv(self)-> float:
        return self._fv
    @fv.setter
    def secies(self, value)-> None:
        self._fv = value
        
    @property
    def fc(self)-> float:
        return self._fc
    @fc.setter
    def secies(self, value)-> None:
        self._fc = value
        
    @property
    def fcp(self)-> float:
        return self._fcp
    @fcp.setter
    def secies(self, value)-> None:
        self._fcp = value
        
    @property
    def ft(self)-> float:
        return self._ft
    @ft.setter
    def secies(self, value)-> None:
        self._ft = value
        
    @property
    def E(self)-> float:
        return self._E
    @E.setter
    def secies(self, value)-> None:
        self._E = value
        
    @property
    def E05(self)-> float:
        return self._E05
    @E05.setter
    def secies(self, value)-> None:
        self._E05 = value

    @property
    def Material_Type(self)-> str:
        return self._mat_type
    @Material_Type.setter
    def Material_Type(self, value)-> None:
        self._mat_type = value
    
    