"""
Module of functions for the Fennel et al. (2006) NPZD 1-D (time, z) toy model.

Inputs can be scalars or vectors (z), except for get_I which expects vectors.
"""

import numpy as np

# Parameters for:

# light
par = 0.43 # fraction of light available for photosynthesis [dimensionless]
K_w = 0.04 # light attenuation coeff. for water [m-1]
K_chl = 0.02486 # light attenuation coeff. for chlorophyll [(mg Chl)-1 m2] (corrected)

# phytoplankton and chlorophyll
#alpha = 0.125 # initial slope of the P-I curve [molC gChl-1 (W m-2)-1 d-1]
alpha = 0.025 # initial slope of the P-I curve [(W m-2)-1 d-1] (ROMS version)
mu_0 = 0.59 # phytoplankton growth rate at 0 degC [d-1]
theta_max = 0.053 # max ratio of chlorophyll to phytoplankton biomass [mg Chl (mg C)-1]
m_P = 0.15 # phytoplankton mortality rate [d-1]
tau = 0.005 # aggregation factor [(mmol N m-3)-1 d-1]
w_P = 0.1 # phytoplankton sinking [m d-1]
k_NO3 = 0.5 # half-saturation concentration for uptake of NO3 [mmol N m-3]
k_NH4 = 0.5 # half-saturation concentration for uptake of NH4 [mmol N m-3]

# detritus
w_S = 0.1 # small detritus sinking [m d-1]
w_L = 1 # large detritus sinking [m d-1]
r_S = 0.03 # remin. rate of small detritus [d-1]
r_L = 0.01 # remin. rate of large detritus [d-1]

# zooplankton
beta = 0.75 # efficiency of assimilation of ingested phytoplankton [dimensionless]
l_BM = 0.1 # excretion rate due to basal metabolism [d-1]
l_E = 0.1 # max rate of assimilation-related excretion [d-1]
m_Z = 0.025 # zooplankton mortality rate [(mmol N m-3)-2 d-1]
g_max = 0.6 # max grazing rate [(mmol N m-3)-1 d-1]
k_P = 2 # half-saturation conc. for phytoplankton ingestion [(mmol N m-3)^2]

# nitrate and ammonimum
n_max = 0.05 # max nitrification rate [d-1] (NH4 -> NO3)
k_E = 0.1 # light intensity at which inhibition of nitrification is half-saturated [W m-2]
Eo = 0.0095 # threshold for light inhibition of nitrification [W m-2]

def get_mu_max(T):
    """
    Max phytoplankton growth rate vs. temp
    Eppley (1972)
    
    Input:
    T = temperature [degC]
    
    Output:
    mu_max = max growth rate [d-1]
    """
    mu_max = mu_0 * 1.066**T
    return mu_max
    
def get_E(swrad0, z_rho, z_w, Chl):
    """
    Profile of photosynthetically available radiation vs. z
    NOTE: all inputs except swrad0 must be vectors (z)
    NOTE: we assume z_rho, z_w, and Chl are packed bottom-to-top
    NOTE: corrected Chl integral to use mean, as per notes in ROMS Forum:
    https://www.myroms.org/forum/viewtopic.php?p=2444&hilit=AttChl+units#p2444
    
    Input:
    swrad0 = incoming swrad at surface [W m-2] (called I_0 in Fennel)
    z_rho = vertical positions of cell centers, positive up, 0 at surface [m]
    z_w = vertical positions of cell boundaries, positive up, 0 at surface [m]
    Chl = chlorophyll concentration profile at cell centers [mg Chl m-3]
    
    Output:
    E = photosynthetically available radiation [W m-2]
    """
    dz = np.diff(z_w)
    N = len(Chl)
    mean_Chl = np.zeros(N)
    for ii in range(N):
        this_dz = dz[ii:]
        this_dz[0] *= 0.5
        this_Chl = Chl[ii:]
        mean_Chl[ii] = np.sum(this_dz * this_Chl) / np.sum(this_dz)
    E = swrad0 * par * np.exp( z_rho * (K_w + K_chl*mean_Chl))
    return E
    
def get_f(E, mu_max):
    """
    The photosynthesis-light relationship, Evans and Parslow (1985).
    
    Input:
    E = photosynthetically available radiation [W m-2]
    mu_max = max growth rate [d-1]
    alpha = initial slope of the P-I curve [molC gChl-1 (W m-2)-1 d-1]
    
    Output:
    f = the P-I curve [dimensionless]
    """
    f = alpha * E / np.sqrt(mu_max**2 + (alpha * E)**2)
    return f
    
def get_L(NO3, NH4):
    """
    Fundamentally this gives the nutrient concentration that is part
    of the phytoplankton growth rate, but it involves the
    Michaelis-Menten functions for nutrient limitation.

    For zero nutrients L = 0.  As the nutrients become large
    compared to their half-saturations L goes to 1.
    And of course L = 1/2 when the nutrient is at its half-saturation.

    Input:
    NO3 = nitrate concentration [mmol N m-3]
    NH4 = ammonium concentration [mmol N m-3] (a cation, NH4+)

    Output:
    L_NO3 and L_NH4 [dimensionless]
    """
    L_NO3 = (NO3 / (k_NO3 + NO3)) * (1 / (1 + (NH4/k_NH4)))
    L_NH4 = (NH4 / (k_NH4 + NH4))
    return L_NO3, L_NH4
    
def get_Ing(Phy):
    """
    Hollings-type s-shaped grazing curve.
    
    Input:
    Phy = phytoplankton [mmol N m-3]
    
    Output:
    Ing = grazing rate [d-1] ("Ingestion" to match Banas terminology)
    """
    Ing = g_max * (Phy**2 / (k_P + Phy**2))
    return Ing
    
def rho_Chl(mu, Phy, E, Chl):
    """
    Calculate the fraction of phytoplankton growth that goes into Chl synthesis.

    Input:
    mu = phytoplankton growth rate [d-1]
    Phy = phytoplankton [mmol N m-3]
    E = photosynthetically available radiation [W m-2]
    Chl = chlorophyll [mg Chl m-3]

    Output:
    rho_Chl = the fraction [dimensionless]
    
    Note on units:
    theta_max: [mg Chl (mg C)-1]
    alpha: [(W m-2)-1 d-1]
    E: [W m-2]
    """
    PhyCN = 6.625 # Phytoplankton Redfield ratio = 106/16 [mol C / mol N]
    Caw = 12 # Carbon atomic weight [g C / mol C]
    rho_Chl = PhyCN * Caw * theta_max * mu * Phy / (alpha * E * Chl)
    return rho_Chl
    
def get_n(E):
    """
    Calculate rate of nitrification (NH4 to NO3), which is light-limited.
    
    Input:
    E = photosynthetically available radiation [W m-2]
    
    Output:
    n = nitrification rate [d-1]
    """
    n = n_max * (1 - np.maximum(0*E, ((E - Eo) / (k_E + E - Eo))))
    return n