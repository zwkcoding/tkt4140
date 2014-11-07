# The equation solved is the parabolic equaiton
#
#       du     d  du
#       -- = k -- --
#       dt     dx dx
#
# along with boundary conditions

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import scipy as sc
import scipy.sparse
import scipy.sparse.linalg
import time
from numpy import newaxis

# change some default values to make plots more readable on the screen
LNWDT = 3; FNT = 15
matplotlib.rcParams['lines.linewidth'] = LNWDT; matplotlib.rcParams['font.size'] = FNT

def explicit_python_solver(u_left=1.0, u_right=0.0, nx=20, r=0.5, xmin=0.0, xmax=1.0, tmin=0.0, tmax=1.0, k=1.0):
    """explicit python solver"""
    dx = float(xmax-xmin)/nx
    u = np.zeros((nx+1, 1), 'd')
    u_old = np.zeros((nx+1, 1), 'd')
    x = np.linspace(xmin,xmax,nx+1)

    # set boundary conditions
    u[0] = u_left
    u_old[-1] = u_right
    
    dt = r*dx**2/k     # compute timestep based on Fourier number, dx and diffusivity
    
    m = round((tmax-tmin)/dt) # number of temporal intervals
    time = np.linspace(tmin,tmax,m)
    
    # advance in time
    for t in time:
        u_old[:] = u[:]
        for i in range(1,nx):
            u[i] = r*(u_old[i-1] + u_old[i+1]) + (1.0 - 2.0*r)*u_old[i]
            
    return x, u

def explicit_numpy_solver(u_left=1.0, u_right=0.0, nx=20, r=0.5, xmin=0.0, xmax=1.0, tmin=0.0, tmax=1.0, k=1.0):
    dx = float(xmax-xmin)/nx
    u = np.zeros((nx+1, 1), 'd')
    x = np.linspace(xmin,xmax,nx+1)

    # set boundary conditions
    u[0] = u_left
    u[-1] = u_right
    
    dt = r*dx**2/k     # compute timestep based on Fourier number, dx and diffusivity
    
    m=round((tmax-tmin)/dt) # number of temporal intervals
    time=np.linspace(tmin,tmax,m)
    
    # advance in time
    for t in time:
        u[1:-1] =  r*(u[0:-2] + u[2:]) + (1.0 - 2.0*r)*u[1:-1]

    return x, u

def implicit_numpy_solver(u_left=1.0, u_right=0.0, nx=20, r=0.5, xmin=0.0, xmax=1.0, tmin=0.0, tmax=1.0, k=1.0, theta=1.0):
    dx = float(xmax-xmin)/nx
    u = np.zeros((nx+1, 1), 'd')
    x = np.linspace(xmin,xmax,nx+1)

    u[0] = u_left
    u[-1] = u_right

    dt = r*dx**2/k     # compute timestep based on Fourier number, dx and diffusivity
 
    m = round((tmax-tmin)/dt) # number of temporal intervals
    time = np.linspace(tmin,tmax,m)

    # create matrix for sparse solver. Solve for interior values only (nx-1)
    diagonals = np.zeros((3,nx-1))   
    diagonals[0,:] = -r*theta                       # all elts in first row is set to 1
    diagonals[1,:] = 1 + 2.0*r*theta  
    diagonals[2,:] = -r*theta 
    As = sc.sparse.spdiags(diagonals, [-1,0,1], nx-1, nx-1,format='csc') # sparse matrix instance

    # create rhs array
    d = np.zeros((nx-1,1),'d')
        
    # advance in time and solve tridiagonal system for each t in time
    for t in time:
        d[:] = u[1:-1] + r*(1 - theta)*(u[0:-2] - 2.0*u[1:-1] + u[2:])  
        d[0] += r*theta*u[0]
        w = sc.sparse.linalg.spsolve(As,d)
        u[1:-1] = w[:,None]

    return x, u

def implicit_numpy_solver_time_evolution(u_left=1.0, u_right=0.0, nx=20, r=0.5, xmin=0.0, xmax=1.0, tmin=0.0, tmax=1.0, k=1.0, theta=1.0):
    dx = float(xmax-xmin)/nx
    u = np.zeros((nx+1, 1), 'd')
    x = np.linspace(xmin,xmax,nx+1)
    

    u[0] = u_left
    u[-1] = u_right

    dt = r*dx**2/k     # compute timestep based on Fourier number, dx and diffusivity
 
    m = round((tmax-tmin)/dt) # number of temporal intervals
    time = np.linspace(tmin,tmax,m)
    #uv = np.zeros((nx+1,m),'d')    
    uv = np.zeros((nx+1,m),'d')
    uv =uv.reshape((nx+1,m))
    uv[0,:] = u_left
    uv[-1,:] = u_right

    

    # create matrix for sparse solver. Solve for interior values only (nx-1)
    diagonals = np.zeros((3,nx-1))   
    diagonals[0,:] = -r*theta                       # all elts in first row is set to 1
    diagonals[1,:] = 1 + 2.0*r*theta  
    diagonals[2,:] = -r*theta 
    As = sc.sparse.spdiags(diagonals, [-1,0,1], nx-1, nx-1,format='csc') # sparse matrix instance

    # create rhs array
    d = np.zeros((nx-1,1),'d')
    
#    print 'd shape:',d.shape, 'and uv[1:-1,i].shape', uv.shape 
#     print 'd flags', d.flags
#     print 'uv flags', uv.flags
#     
    # advance in time and solve tridiagonal system for each t in time
    for i, t in enumerate(time):
         
        d[:] = (uv[1:-1,i] + r*(1 - theta)*(uv[0:-2,i] - 2.0*uv[1:-1,i] + uv[2:,i])).reshape(nx-1,1)  
        d[0] += r*theta*uv[0,i]
        w = sc.sparse.linalg.spsolve(As,d)
        uv[1:-1,i] = w[:,]

    return x, time, uv

## Main program starts here

nx = 20 # number of nodes
L  = 1.0    # length of beam
tmax = 0.025    # time length
theta = 0.75    # paramet    er for implicitness: theta=0.5 Crank-Nicholson, theta=1.0 fully implicit


solvernames = [explicit_python_solver,explicit_numpy_solver,implicit_numpy_solver]

lstyle = ['r-', ':', '.', '-.', '--']
i = 0
legends=[]

for solve in solvernames:
    tic = time.time()
    x, u = solve(u_left=100.0, u_right=0.0, nx=nx, r=0.5, xmin=0.0, xmax=L, tmin=0.0, tmax=tmax, k=1.0)
    toc = time.time()
    cputime = toc - tic
    legends.append(solve.__name__)
    print legends[i], '\t cpu time = ', cputime 
    plt.plot(x,u,lstyle[i])
    i += 1


x, t, uv = implicit_numpy_solver_time_evolution(u_left=100.0, u_right=0.0, nx=nx, r=0.5, xmin=0.0, xmax=L, tmin=0.0, tmax=tmax, k=1.0)
plt.plot(x,uv[:,len(t)-1])

plt.legend(legends)
plt.title('Temperature field')
plt.xlabel('Position on beam')
plt.ylabel('Temperature')
#plt.savefig('1dheat0_025.pdf')
plt.show()
