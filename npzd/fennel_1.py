"""
First 1-D Fennel model.  Calculates time-evolution of the 7 state
variables as a function of z, given some initial condition and light.
"""

import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
import fennel_functions as ff
from importlib import reload
reload(ff)

# z-coordinates (bottom to top, positive up)
N = 50 # number of vertical grid cells
H = 100 # max depth [m]
z_w = np.linspace(-H,0,N+1)
dz = np.diff(z_w)
z_rho = z_w[:-1] + dz/2

# time
tmax = 100 # max time [days]
# calculate timestep dynamically
# dt <= stability_factor * dz / w_L
stability_factor = 0.1 # empirical, must be < 1
dt = np.floor(1000 * stability_factor * np.min(dz) / ff.w_L) / 1000
dt = np.min((0.05, dt))
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
vn_list = ['Phy', 'Chl', 'Zoo', 'SDet', 'LDet', 'NO3', 'NH4']
Omat = np.nan * np.ones((NT, N))
V = dict()
for vn in vn_list:
    V[vn] = Omat.copy()
    
# initialize dict of reservoir time series
vnr_list = ['Phy', 'Zoo', 'SDet', 'LDet', 'NO3', 'NH4', 'Lost']
R = dict()
for vn in vnr_list:
    R[vn] = np.nan * np.ones(NTR)
    
# intial conditions, all [mmol N m-3] except Chl
v = dict()
v['Phy'] = 0.01 * np.ones(N)
v['Chl'] = 2.5 * v['Phy'].copy() # [mg Chl m-3]
v['Zoo'] = 0.1 * v['Phy'].copy()
v['SDet'] = 0 * np.ones(N)
v['LDet'] = 0 * np.ones(N)
v['NO3'] = 20 * np.ones(N)
v['NH4'] = 0 * np.ones(N)

T = 10 * np.ones(N) # temperature [degC] vs. z
swrad0 = 500 # surface swrad [W m-3]

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
            if vn == 'Chl':
                pass
            else:
                net_N += np.sum(dz * v[vn])
        net_N += denitrified
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
    mu_max = ff.get_mu_max(T)
    I = ff.get_I(swrad0, z_rho, z_w, v['Chl'])
    f = ff.get_f(I, mu_max)
    L_NO3, L_NH4 = ff.get_L(v['NO3'], v['NH4'])
    L = L_NO3 + L_NH4
    mu = mu_max * f * L
    growth_P = mu * v['Phy']
    #  grazing
    g = ff.get_g(v['Phy'])
    grazing_P = g * v['Zoo']
    # mortality
    mortality_P = ff.m_P * v['Phy']
    #  coagulation to large detrius
    coag_P = ff.tau * (v['SDet'] + v['Phy']) * v['Phy']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['Phy'])
    dc[-1] = - v['Phy'][-1]
    sink_P = ff.w_P * dc / dz
    # net change
    dv['Phy'] = dt * (growth_P - grazing_P - mortality_P - coag_P + sink_P)
    
    # Chl: chlorophyll
    # growth
    rho_Chl = ff.rho_Chl(mu, v['Phy'], I, v['Chl'])
    growth_Ch = rho_Chl * mu * v['Chl']
    # grazing
    grazing_Ch = g * v['Zoo'] * v['Chl'] / v['Phy']
    #  mortality
    mortality_Ch = ff.m_P * v['Chl']
    # coagulation to large detrius
    coag_Ch = ff.tau * (v['SDet'] + v['Phy']) * v['Chl']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['Chl'])
    dc[-1] = - v['Chl'][-1]
    sink_Ch = ff.w_P * dc / dz
    # net change
    dv['Chl'] = dt * (growth_Ch - grazing_Ch - mortality_Ch - coag_Ch + sink_Ch)
    
    # Zoo: zooplankton
    # growth
    growth_Z = g * ff.beta * v['Zoo']
    # excretion
    excretion_Z = (ff.l_BM + (ff.l_E * ff.beta * v['Phy']**2 / (ff.k_P + v['Phy']**2))) * v['Zoo']
    # mortality
    mortality_Z = ff.m_Z * v['Zoo']**2
    # net change
    dv['Zoo'] = dt * (growth_Z - excretion_Z - mortality_Z)
    
    # SDet: small detritus
    # sloppy eating
    egestion_S = g * (1 - ff.beta) * v['Zoo']
    # coagulation to large detrius
    coag_S = ff.tau * (v['SDet'] + v['Phy']) * v['SDet']
    # remineralization
    remin_S = ff.r_S * v['SDet']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['SDet'])
    dc[-1] = - v['SDet'][-1]
    sink_S = ff.w_S * dc / dz
    # net change
    dv['SDet'] = dt * (egestion_S + mortality_P + mortality_Z - coag_S - remin_S + sink_S)
    
    # LDet: large detritus
    # remineralization
    remin_L = ff.r_L * v['LDet']
    # sinking
    dc = np.zeros(N)
    dc[0:-1] = np.diff(v['LDet'])
    dc[-1] = - v['LDet'][-1]
    sink_L = ff.w_L * dc / dz
    # net change
    dv['LDet'] = dt * (coag_P + coag_S - remin_L + sink_L)
    
    # NO3: nitrate
    # uptake
    uptake_NO3 = mu_max * f * L_NO3 * v['Phy']
    # nitrification
    n = ff.get_n(I)
    nitrification = n * v['NH4']
    # net_change
    dv['NO3'] = dt * (-uptake_NO3 + nitrification)
    
    # NH4: ammomium
    # uptake
    uptake_NH4 = mu_max * f * L_NH4 * v['Phy']
    # net change
    dv['NH4'] = dt * (-uptake_NH4 - nitrification + excretion_Z + remin_S + remin_L)
    # bottom boundary layer
    max_denitrification = dt * (1 / dz[0]) * (ff.w_P*v['Phy'][0] + ff.w_S*v['SDet'][0] + ff.w_L*v['LDet'][0])
    denit_fac = 0.25 # fraction of particle flux at bottom that is returned to NH4, 4/16
    dv['NH4'][0] += denit_fac * max_denitrification
    
    # update all variables
    for vn in vn_list:
        v[vn] += dv[vn]
    denitrified += dz[0] * (1 - denit_fac) * max_denitrification
    
        
# plotting
#plt.close('all')
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
    
    
