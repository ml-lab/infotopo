from scipy.integrate import ode
import numpy as np

def callback_func(t, x, v):
    return True
    
class geodesic(ode):

    def __init__(self, r, j, Avv, M, N, x, v, lam = 0.0, dtd = None, atol = 1e-6, rtol = 1e-6, callback = None, parameterspacenorm = False):
        self.r, self.j, self.Avv = r, j, Avv
        self.M, self.N = M, N
        self.lam = lam
        if dtd is None:
            self.dtd = np.eye(N)
        else:
            self.dtd = dtd
        self.atol = atol
        self.rtol = rtol
        ode.__init__(self, self.geodesic_rhs, jac = None)
        self.set_initial_value(x, v)
        ode.set_integrator(self, 'vode', atol = atol, rtol = rtol)
        if callback is None:
            self.callback = callback_func
        else:
            self.callback = callback
        self.parameterspacenorm = parameterspacenorm

    def geodesic_rhs(self, t, xv):
        x = xv[:self.N]
        v = xv[self.N:]
        j = self.j(x)
        g = np.dot(j.T, j) + self.lam*self.dtd
        Avv = self.Avv(x, v)
        a = -np.linalg.solve(g, np.dot(j.T, Avv) )
        if self.parameterspacenorm:
            a -= np.dot(a,v)*v/np.dot(v,v)
        return np.append(v, a)
                                              
    def set_initial_value(self, x, v):
        self.xs = np.array([x])
        self.vs = np.array([v])
        self.ts = np.array([0.0])
        self.rs = np.array([ self.r(x) ] )
        self.vels = np.array([ np.dot(self.j(x), v) ] )
        ode.set_initial_value( self, np.append(x, v), 0.0 )

    def step(self, dt = 1.0):
        ode.integrate(self, self.t + dt, step = 1)
        self.xs = np.append(self.xs, [self.y[:self.N]], axis = 0)
        self.vs = np.append(self.vs, [self.y[self.N:]], axis = 0 )
        self.rs = np.append(self.rs, [self.r(self.xs[-1])], axis = 0)
        self.vels = np.append(self.vels, [np.dot(self.j(self.xs[-1]), self.vs[-1])], axis = 0)
        self.ts = np.append(self.ts, self.t)

    def integrate(self, tmax, maxsteps = 500):
        cont = True
        while self.successful() and len(self.xs) < maxsteps and self.t < tmax and cont:
            self.step(tmax - self.t)
            cont = self.callback(self.t, self.y[:self.N], self.y[self.N:])

            
                
        
