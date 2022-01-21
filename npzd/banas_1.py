"""
First 1-D Banas model.  Calculates time-evolution of the 5 state
variables as a function of z, given some initial condition and light.
"""

import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
import banas_functions as bnf
from importlib import reload
reload(bnf)

# z-coordinates (bottom to top, positive up)
N = 50 # number of vertical grid cells
H = 100 # max depth [m]
z_w = np.linspace(-H,0,N+1)
dz = np.diff(z_w)
z_rho = z_w[:-1] + dz/2

# time
tmax = 10 # max time [days]
dt = .001 # time step [days]
tvec = np.arange(0, tmax+dt, dt)
nt = len(tvec)
# times to save results for profiles
DT = tmax/10
Tvec = np.arange(0, tmax+DT, DT)
NT = len(Tvec)
# times to save results for net amounts
DTR = tmax/100
TRvec = np.arange(0, tmax+DTR, DTR)
NTR = len(TRvec)

# initialize dict of output arrays
vn_list = ['Phy', 'Zoo', 'SDet', 'LDet', 'NO3']
Omat = np.nan * np.ones((NT, N))
V = dict()
for vn in vn_list:
    V[vn] = Omat.copy()
    
# initialize dict of reservoir time series
vnr_list = ['Phy', 'Zoo', 'SDet', 'LDet', 'NO3', 'Lost']
R = dict()
for vn in vnr_list:
    R[vn] = np.nan * np.ones(NTR)
    
# intial conditions, all [mmol N m-3] = [uM N]
v = dict()
v['Phy'] = 0.01 * np.ones(N)
v['Zoo'] = 0.1 * v['Phy'].copy()
v['SDet'] = 0 * np.ones(N)
v['LDet'] = 0 * np.ones(N)
v['NO3'] = 20 * np.ones(N)

S = 30 * np.ones(N) # salinity [psu] vs. z
swrad_0 = 500 # surface swrad [W m-3]
E_surface = swrad_0 * 0.43 # surface PAR [W m-2]

tt = 0
ttr = 0
denitrified = 0
dv = dict() # stores the net change vectors
days = []
for t in tvec:
    
    # save output vectors if it is time
    if np.mod(t, DT) == 0:
        print('tt = %d' % (tt))
        for vn in vn_list:
            V[vn][tt,:] = v[vn]
        tt += 1
        # report on global conservation
        net_N = 0
        for vn in vn_list:
            net_N += np.sum(dz * v[vn])
        net_N -= denitrified
        print(' mean N = %0.3f [mmol N m-3]' % (net_N/H))
        
    # save reservoir output if it is time
    if np.mod(t, DTR) == 0:
        for vn in vnr_list:
            if vn == 'Lost':
                R[vn][ttr] = denitrified
            else:
                R[vn][ttr] = np.sum(dz * v[vn])
        ttr += 1
    
    # Phy: phytoplankton
    # growth
    E = bnf.get_E(E_surface, z_rho, z_w, v['Phy'], S)
    f = bnf.get_f(E)
    L = bnf.get_L(v['NO3'])
    mu = bnf.mu_0 * f * L
    growth_P = mu * v['Phy']
    #  grazing
    I = bnf.get_I(v['Phy'])
    grazing_P = I * v['Zoo']
    # mortality
    mortality_P = bnf.m * v['Phy']
    # net change
    dv['Phy'] = dt * (growth_P - grazing_P - mortality_P)
        
    # Zoo: zooplankton
    # growth
    growth_Z = bnf.epsilon * I * v['Zoo']
    # mortality
    mortality_Z = bnf.epsilon * v['Zoo']**2
    # net change
    dv['Zoo'] = dt * (growth_Z - mortality_Z)
    
    # SDet: small detritus
    # egestion
    egestion_S = (1 - bnf.epsilon) * bnf.f_egest * I * v['Zoo']
    # coagulation to large detrius
    coag_S = bnf.tau * v['SDet']**2
    # remineralization
    remin_S = bnf.r * v['SDet']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['SDet'])
    dc[-1] = - v['SDet'][-1]
    sink_S = bnf.w_S * dc / dz
    # net change
    dv['SDet'] = dt * (egestion_S + mortality_P + mortality_Z - coag_S - remin_S + sink_S)
    
    # LDet: large detritus
    # remineralization
    remin_L = bnf.r * v['LDet']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['LDet'])
    dc[-1] = - v['LDet'][-1]
    sink_L = bnf.w_L * dc / dz
    # net change
    dv['LDet'] = dt * (coag_S - remin_L + sink_L)
    
    # NO3: nitrate
    # egestion
    egestion_N = (1 - bnf.epsilon) * (1 - bnf.f_egest) * I * v['Zoo']
    # water column denitrification
    # TO-DO: needs oxygen
    # net_change
    dv['NO3'] = dt * (-growth_P + egestion_N + remin_S + remin_L)
    # bottom boundary layer
    denitrification = dt * (1 / dz[0]) * np.min((bnf.chi, bnf.w_S*v['SDet'][0] + bnf.w_L*v['LDet'][0]))
    #denitrification = dt * (1 / dz[0]) * bnf.chi
    dv['NO3'][0] -= denitrification
    
    # update all variables
    for vn in vn_list:
        v[vn] += dv[vn]
    denitrified += dz[0] * denitrification
        
# plotting
plt.close('all')
pfun.start_plot(fs=8, figsize=(18,11))

fig, axes = plt.subplots(nrows=1, ncols=7, squeeze=False)
ii = 0
for vn in vn_list:
    ax = axes[0,ii]
    vv = V[vn]
    for tt in range(NT):
        ax.plot(vv[tt,:], z_rho, lw=(tt+1)/4)
        if ii == 0:
            ax.set_ylabel('Z [m]')
        if ii > 0:
            ax.set_yticklabels([])
    ax.set_title(vn)
    ii += 1
    
fig = plt.figure(figsize=(14,8))
ax = fig.add_subplot(111)
for vn in vnr_list:
    ax.plot(TRvec, R[vn], label=vn, lw=2)
ax.legend()
ax.grid(True)
ax.set_xlabel('Days')
ax.set_ylabel('Net N [mmol N m-2]')
    
plt.show()
pfun.end_plot()
    
    
