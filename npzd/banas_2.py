"""
First 1-D Banas model.  Calculates time-evolution of the 5 state
variables as a function of z, given some initial condition and light.

Like banas_1.py but with a new treatment of sinking.
"""

import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
import banas_functions as bnf
import shared
from importlib import reload
reload(bnf)
reload(shared)

# z-coordinates (bottom to top, positive up)
H = shared.H # max depth [m]
N = shared.N # number of vertical grid cells
Dz = H/N
z_w = np.arange(-H,Dz,Dz)
z_rho = z_w[:-1] + Dz/2

# time
tmax = shared.tmax # max time [days]
dt = .002

# number of time steps
nt = int(np.round(tmax/dt))
# number of time steps between saves of profiles
ntp = int(np.round((tmax/10)/dt))
Ntp = int(np.round((nt/ntp))) + 1 # total number of saved profiles
# number of time steps between saves of net amounts (reservoirs)
ntr = int(np.round((tmax/100)/dt))
Ntr = int(np.round((nt/ntr))) + 1 # total number of saved net amounts

# initialize dict of output arrays
vn_list = ['Phy', 'Zoo', 'SDet', 'LDet', 'NO3']
Omat = np.nan * np.ones((Ntp, N))
V = dict()
for vn in vn_list:
    V[vn] = Omat.copy()
V['I'] = np.nan * np.ones((Ntp, N))
    
# initialize dict of reservoir time series
vnr_list = ['Phy', 'Zoo', 'SDet', 'LDet', 'NO3', 'Lost']
R = dict()
for vn in vnr_list:
    R[vn] = np.nan * np.ones(Ntr)
    
# intial conditions, all [mmol N m-3] = [uM N]
v = dict()
v['Phy'] = 0.01 * np.ones(N)
v['Zoo'] = 0.1 * v['Phy'].copy()
v['SDet'] = 0 * np.ones(N)
v['LDet'] = 0 * np.ones(N)
v['NO3'] = 20 * np.ones(N)

S = 32 * np.ones(N) # salinity [psu] vs. z
swrad0 = 500 # surface swrad [W m-3]

Wsink_dict = {'SDet':bnf.w_S, 'LDet':bnf.w_L}

denitrified = 0
dv = dict() # stores the net change vectors
TRvec = []
it = 0
itp = ntp
Itp = 0
itr = ntr
Itr = 0
while it <= nt:
    
    # save output vectors if it is time
    if itp == ntp:
        print('t = %0.2f days' % (it*dt))
        for vn in vn_list:
            V[vn][Itp,:] = v[vn]
        V['I'][Itp,:] = bnf.get_E(swrad0, z_rho, z_w, v['Phy'], S)
        # report on global conservation
        net_N = 0
        for vn in vn_list:
            if vn == 'Chl':
                pass
            else:
                net_N += np.sum(Dz * v[vn])
        net_N += denitrified
        print(' mean N = %0.3f [mmol N m-3]' % (net_N/H))
        itp = 0
        Itp += 1
    # save reservoir output if it is time
    if itr == ntr:
        TRvec.append(it*dt)
        for vn in vnr_list:
            if vn == 'Lost':
                R[vn][Itr] = denitrified
            else:
                R[vn][Itr] = np.sum(Dz * v[vn])
        itr = 0
        Itr += 1
    
    # Phy: phytoplankton
    # growth
    E = bnf.get_E(swrad0, z_rho, z_w, v['Phy'], S)
    f = bnf.get_f(E)
    L = bnf.get_L(v['NO3'])
    mu = bnf.mu_0 * f * L
    growth_P = mu * v['Phy']
    #  grazing
    Ing = bnf.get_Ing(v['Phy'])
    grazing_P = Ing * v['Zoo']
    # mortality
    mortality_P = bnf.m * v['Phy']
    # net change
    dv['Phy'] = dt * (growth_P - grazing_P - mortality_P)
        
    # Zoo: zooplankton
    # growth
    growth_Z = bnf.epsilon * Ing * v['Zoo']
    # mortality
    mortality_Z = bnf.xi * v['Zoo']**2
    # net change
    dv['Zoo'] = dt * (growth_Z - mortality_Z)
    
    # SDet: small detritus
    # egestion
    egestion_S = (1 - bnf.epsilon) * bnf.f_egest * Ing * v['Zoo']
    # coagulation to large detrius
    coag_S = bnf.tau * v['SDet']**2
    # remineralization
    remin_S = bnf.r * v['SDet']
    # net change
    dv['SDet'] = dt * (egestion_S + mortality_P + mortality_Z - coag_S - remin_S)
    
    # LDet: large detritus
    # remineralization
    remin_L = bnf.r * v['LDet']
    # net change
    dv['LDet'] = dt * (coag_S - remin_L)
    
    # NO3: nitrate
    # egestion
    egestion_N = (1 - bnf.epsilon) * (1 - bnf.f_egest) * Ing * v['Zoo']
    # net_change
    dv['NO3'] = dt * (-growth_P + egestion_N + remin_S + remin_L)
    
    # update all variables
    for vn in vn_list:
        v[vn] += dv[vn]
        v[vn][v[vn]<0] = 0
    
    # sinking
    max_denitrification = 0
    for vn in ['SDet', 'LDet']:
        C = v[vn]
        Wsink = Wsink_dict[vn]
        Cnew, Cnet_lost = shared.sink(z_w, z_rho, Dz, N, C, Wsink, dt)
        v[vn] = Cnew
        max_denitrification += Cnet_lost / Dz
    
    # bottom boundary layer
    # (i) instant remineralization of all sinking particles
    v['NO3'][0] += max_denitrification
    # (ii) some benthic loss
    denitrification = 0#dt*bnf.chi/Dz
    v['NO3'][0] -= denitrification
    
    denitrified += Dz * denitrification
        
    it += 1
    itp += 1
    itr += 1
        
# plotting
#plt.close('all')
pfun.start_plot(fs=8, figsize=(16,6))

fig, axes = plt.subplots(nrows=1, ncols=len(V.keys()), squeeze=False)
ii = 0
for vn in V.keys():
    ax = axes[0,ii]
    vv = V[vn]
    for tt in range(Ntp):
        ax.plot(vv[tt,:], z_rho, lw=(tt+1)/4)
        if ii == 0:
            ax.set_ylabel('Z [m]')
        if ii > 0:
            ax.set_yticklabels([])
    ax.set_title(vn)
    ii += 1
    
fig = plt.figure(figsize=(16,6))
ax = fig.add_subplot(211)
for vn in vnr_list:
    if vn == 'NO3':
        pass
    else:
        ax.plot(TRvec, R[vn], label=vn, lw=2)
ax.legend()
ax.grid(True)
#ax.set_xlabel('Days')
ax.set_ylabel('Net N [mmol N m-2]')
ax = fig.add_subplot(212)
for vn in ['NO3']:
    ax.plot(TRvec, R[vn], label=vn, lw=2)
ax.legend()
ax.grid(True)
ax.set_xlabel('Days')
ax.set_ylabel('Net N [mmol N m-2]')
    
plt.show()
pfun.end_plot()
    
    
