"""
Code to explore the Fennel et al. (2006) NPZD model equations.
"""

import matplotlib.pyplot as plt
import numpy as np
from lo_tools import plotting_functions as pfun

def get_mu_max(T, mu_0=0.69):
    """
    Max phytoplankton growth rate vs. temp
    Eppley (1972)
    
    Input:
        T = temperature [degC]
        mu_0 = phytoplankton growth rate at 0 degC [d-1]
    Output:
        mu_max = max growth rate [d-1]
    """
    mu_max = mu_0 * 1.066**T
    return mu_max
    
def get_I(I_0, z_rho, z_w, Chl, par=0.43, K_w=0.04, K_chl=0.025):
    """
    Profile of photosynthetically available radiation vs. z
    NOTE: we assume z_w and Chl are packed bottom-to-top
    
    Input:
        I_0 = incoming swrad at surface [W m-2?]
        z_w = vertical positions of cell boundaries, positive up, 0 at surface [m]
        Chl = chlorophyll concentration profile at cell centers [units??]
        par = fraction of light available for photosynthesis [dimensionless]
        K_w = light attenuation coeff. for water [m-1]
        K_chl = light attenuation coeff. for chlorophyll [(mg Chl)-1 m-2]
    Output:
        I = photosynthetically available radiation [W m-2?]
    """
    dz = np.diff(z_w)
    N = len(Chl)
    int_Chl = np.zeros(N)
    for ii in range(N):
        this_dz = dz[ii:]
        this_dz[0] *= 0.5
        this_Chl = Chl[ii:]
        int_Chl[ii] = np.sum(this_dz * this_Chl)
    I = I_0 * par * np.exp( z_rho * (K_w + K_chl*int_Chl))
    return I
    
def get_f(I, mu_max, alpha=0.125):
    """
    The photosynthesis-light relationship, evans and Parslow (1985).
    
    Input:
        I = photosynthetically available radiation [W m-2?]
        mu_max = max growth rate [d-1]
        alpha = initial slope of the P-I curve [molC gChl-1 (W m-2)-1 d-1]
    """
    f = alpha * I / np.sqrt(mu_max**2 + (alpha * I)**2)
    return f
    
def get_L(NO3, NH4, k_NO3=0.5, k_NH4=0.5):
    """
    Fundamentally this gives the nutrient concentration that is part
    of the phytoplankton growth rate, but it involves the
    Michaelis-Menten functions for nutrient limitation.

    For zero nutrients L = 0.  As the nutrients become large
    compared to their half-saturations L goes to 1.

    Input:
    NO3 = nitrate concentration [mmol N m-3]
    NH4 = ammonium concentration [mmol N m-3] (a cation, NH4+)
    k_NO3 = half-saturation concentration for uptake of NO3 [mmol N m-3]
    k_NH4 = half-saturation concentration for uptake of NH4 [mmol N m-3]

    Output:
    L = L_NO3 + L_NH4 [dimensionless]
    """
    L_NO3 = (NO3 / (k_NO3 + NO3)) * (1 / (1 + (NH4/k_NH4)))
    L_NH4 = (NH4 / (k_NH4 + NH4))
    L = L_NO3 + L_NH4
    return L

plt.close('all')
pfun.start_plot(fs=10, figsize=(18,10))

fig, axes = plt.subplots(nrows=2, ncols=2)

# example calculations to look at functional dependence

# mu_max(T)
T = np.linspace(0,25,100)
mu_max = get_mu_max(T)
#
ax = axes[0,0]
ax.plot(T, mu_max, '-b', lw=3)
ax.set_xlabel('Temperature [degC]')
ax.set_ylabel('mu_max [d-1]')
ax.text(.05,.9,'Max Phytoplankton Growth Rate vs. T',transform=ax.transAxes)
ax.grid(True)
ax.set_ylim(bottom=0)

# I(z) with and without Chl
I_0 = 500
z_w = np.linspace(-30,0,101)
z_rho = z_w[:-1] + np.diff(z_w)/2
Chl = np.linspace(1,2,len(z_rho))
I = get_I(I_0, z_rho, z_w, Chl)
Iclean = get_I(I_0, z_rho, z_w, 0*Chl)
#
ax = axes[0,1]
ax.plot(I, z_rho, '-', c='orange', lw=3, label='With Chl')
ax.plot(Iclean, z_rho, '-', c='cyan', lw=3, label='No Chl')
ax.legend()
ax.set_xlabel('I [W m-2]')
ax.set_ylabel('Z [m]')
ax.text(.05,.9,'Light vs. Z',transform=ax.transAxes)
ax.grid(True)

# f(I)
I = np.linspace(0,100,100)
T = 10 * np.ones(len(I))
f = get_f(I, get_mu_max(T))
#
ax = axes[1,0]
ax.plot(I, f, '-', c='purple', lw=3)
ax.set_xlabel('I [W m-2]')
ax.set_ylabel('f(I)')
ax.text(.05,.9,'P-I Curve',transform=ax.transAxes)
ax.grid(True)

# L(NO3, NH4)
NO3 = np.linspace(0,30,100)
NH4 = 0 * NO3
L = get_L(NO3, NH4)
NH4 = 0.1 * NO3
LL = get_L(NO3, NH4)
#
ax = axes[1,1]
ax.plot(NO3, L, '-', c='brown', lw=3, label='NH4=0')
ax.plot(NO3, LL, '-', c='gold', lw=3, label='NH4=0.1*NO3')
ax.legend()
ax.set_xlabel('NO3 [mmol N m-3]')
ax.set_ylabel('L')
ax.text(.05,.9,'M-M Curve',transform=ax.transAxes)
ax.grid(True)

plt.show()
pfun.end_plot()
