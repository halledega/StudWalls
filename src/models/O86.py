from .section import Section
from math import sqrt, log10

class O86_20:    
    
    @staticmethod
    def CL5_3_2_2(Duration = 'Standard', Pl = 0, Ps = 0):
        if Pl > Ps and Ps > 0:
            kd = O86_20.CL5_3_2_3(Pl, Ps)
        elif Pl > Ps and Ps == 0:
            kd = 0.65
        elif Duration == 'Short':
            kd = 1.15
        elif Duration == 'Standard':
            kd = 1.0
        elif Duration == 'Long':
            kd = 0.65
        return kd
    
    @staticmethod
    def CL5_3_2_3(Pl, Ps):
        return min(1.0,max(1.0-0.5*log10(Pl/Ps),0.65))
    
    @staticmethod
    def CL6_5_6_2_2(h: float, b: float) -> float:
        '''
        name: CL6_5_6_2_2
        description: Clause 6.5.2.2 Constant Rectangular Cross-Section. Returns height/width ratio of cross section
        args: h: float; member height, b: float; memeber width
        reurn: b/h: float
        '''
        return h/b
    
    @staticmethod
    def CL6_5_6_2_3(section: Section, Lu: float, **kwargs) -> float:
        '''
        name: CL6_5_6_2_3
        description: Clause 6.5.2.3 Factored Compressive Resistance Parallel to Grain.
        args: section: Section, Lu
        **kwargs: Kd, Kh, Kse, Ksc, Kt
        returns: {'Pr': Pr, "Fc": Fc, "Kzc": Kzc, "Kc": Kc}
        '''
        phi = 0.8 #sawn lumber        
        Kd = kwargs['Kd']
        Kh = kwargs['Kh']
        Kse = kwargs['Kse']
        Ksc = kwargs['Ksc']
        Kt = kwargs['Kt']
        
        design_area = (section.Plys * section.Width) * section.Depth

        if section.Material.Material_Type == 'MSR':
            E05 = 0.85 * section.Material.E05
        elif section.Material.Material_Type == 'MEL':
            E05 = 0.75 * section.Material.E05
        
        Cc = O86_20.CL6_5_6_2_2(Lu, section.Depth)
        
        Fc = section.Material.fc*(Kd * Kh * Ksc * Kt)
                                  
        Kzc = min(6.3*(section.Depth * Lu)**-0.13,1.3)
        
        Kc = (1.0 + (Fc * Kzc * Cc**3)/(35 * section.Material.E05 * Kse * Kt))**-1
               
        if Cc > 50:
            Pr = 0
        else:
            Pr = phi * Fc * design_area * Kc * Kzc
 
        return {'Pr': Pr, "Fc": Fc, "Kzc": Kzc, "Kc": Kc, 'Cc': Cc}
    
#methods below are for spaced compression members
    @staticmethod
    def CLA6_5_6_3_7(Cc: float, section, **kwargs) -> list[float]:
        Fc = kwargs['Fc'] 
        Kse = kwargs['Kse']
        Ke = kwargs['Ke']
        Kt = kwargs['Kt']
        
        if section.material.mat_type == "Sawn" or section.material.mat_type == "MSR" or section.material.mat_type == "MEL":
            phi = 0.8
            k = 1.8
        else:
            phi = 0.9
            k = 2.0
            
        if section.material.mat_type == 'MSR':
            E05 = 0.85 * section.material.E05
        elif section.material.mat_type  == 'MEL':
            E05 = 0.75 * section.material.E05
        else:
            E05 = section.material.E05
        
        Ck = sqrt((0.76 * E05 * Kse * Ke * Kt)/Fc)
        
        if Cc <= 10:
            Kc = 1.0
        elif Cc > 10 and Cc <= Ck:
            Kc = 1 - (1/3)*(Cc/Ck)**4
        elif Cc > Ck and Cc < 80:
            Kc = (E05 * Kse * Ke * Kt)/(k * (Cc**2) * Fc)
        else:
            Kc = 0.0
            
        return phi, Kc

    @staticmethod
    def CLA6_5_6_3_6(section, **kwargs) -> float:
      
        Kd = kwargs['Kd']
        Ksc = kwargs['Ksc']
        Kt = kwargs['Kt']
        l = kwargs['l']
        
        Fc = section.material.fc*(Kd * Ksc * Kt)
        Cc = l/section.d
        
        Kzc = min(6.3*(section.d * l)**-0.13,1.3)
        
        Kc, phi = O86_20.CLA6_5_6_3_7(Cc, section, Fc = Fc, Kse = 1.0, Ke = 1.0, Kt = 1.0)
        
        Pr = phi * Fc * section.A * Kc * Kzc
        
        return {'Pr': Pr, 'Fc': Fc, 'Kc': Kc, 'Kzc': Kzc}
            
    
    