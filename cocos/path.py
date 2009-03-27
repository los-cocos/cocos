class Path:
    def at(self, t):
        pass
        
class Bezier(Path):
    def __init__(self, a, b, ac, bc):
        self.a = a
        self.b = b
        self.ac = ac
        self.bc = bc
        
    def at(self, t):
        def calc(i):
            a = self.a[i]
            b = self.ac[i]
            c = self.bc[i]
            d = self.b[i]
            return ( 
                ((1-t)**3) * a + 
                3*t*((1-t)**2)*b + 
                3*(t**2)*(1-t)*c +
                (t**3)*d
                )
        return calc(0), calc(1)
        
    def __repr__(self):
        return "Bezier( (%i,%i), (%i,%i), (%i, %i), (%i,%i) )"%(
                self.a[0], self.a[0],
                self.b[0], self.b[1],
                self.ac[0], self.ac[1],
                self.bc[0], self.bc[1],

            )
    
