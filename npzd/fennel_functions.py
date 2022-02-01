"""
Module of functions for the Fennel et al. (2006) NPZD 1-D (time, z) toy model.

Inputs can be scalars or vectors (z), except for get_I which expects vectors.
"""

import numpy as np

# copied and edited for python from bio_Fennel.in

# ---------------------------------------------------------------------

# Light attenuation due to seawater [1/m], {0.04}.

AttSW = 0.04

# Light attenuation by chlorophyll [1/(mg_Chl m2)], {0.02486}.

AttChl = 0.02486

# Fraction of shortwave radiation that is photosynthetically active
# (nondimensional), {0.43}.

PARfrac = 0.43

# Eppley temperature-limited growth parameter [nondimensional], {1.0}

Vp0 = 1.0

# Radiation threshold for nitrification inhibition [Watts/m2], {0.0095}.

I_thNH4 = 0.0095

# Half-saturation radiation for nitrification inhibition [Watts/m2], {0.036}.

D_p5NH4 = 0.1

# Nitrification rate: oxidation of NH4 to NO3 [1/day], {0.05}.

NitriR = 0.05

# Inverse half-saturation for phytoplankton NO3 uptake [1/(millimole_N m-3)],
# {2.0}.

K_NO3 = 2.0

# Inverse half-saturation for phytoplankton NH4 uptake [1/(millimole_N m-3)],
# {2.0}.

K_NH4 = 2.0

# Inverse half-saturation for phytoplankton PO4 uptake [1/(millimole_P m-3)],
# {333.0}.

K_PO4 = 32.0

# Zooplankton half-saturation constant (squared) for ingestion
# [millimole_N m-3]^2, {1.0}.

K_Phy = 2.0

# Maximum chlorophyll to carbon ratio [mg_Chl/mg_C], {0.0535}.

Chl2C_m = 0.0535

# Chlorophyll minimum threshold value [mg_Chl/m3], {0.0}.

ChlMin = 0.001

# Phytoplankton Carbon:Nitrogen ratio [mole_C/mole_N] , {6.625}.

PhyCN = 6.625

# Phytoplankton Phosphorus:Nitrogen ratio [mole_P/mole_N] , {0.0625}.

R_P2N = 0.0625

# Phytoplankton, NH4 inhibition parameter [1/(millimole_N)], {1.5}.

PhyIP = 1.5

# Phytoplankton, initial slope of P-I curve [1/(Watts m-2 day)],
# {0.025}.

PhyIS = 0.025

# Phytoplankton minimum threshold value [millimole_N/m3], {0.0}.

PhyMin = 0.001

# Phytoplankton mortality rate [1/day], {0.072}.

PhyMR = 0.15

# Zooplankton Nitrogen assimilation efficiency [nondimesnional], {0.75}.

ZooAE_N = 0.75

# Zooplankton Basal metabolism [1/day], {0.1}.

ZooBM = 0.1

# Zooplankton Carbon:Nitrogen ratio [mole_C/mole_N], {5.0}.

ZooCN = 6.625

# Zooplankton specific excretion rate [1/day], {0.1}.

ZooER = 0.1

# Zooplankton maximum growth rate [1/day], {0.75}.

ZooGR = 0.6

# Zooplankton minimum threshold value [millimole_N/m3], {0.0}.

ZooMin = 0.001

# Zooplankton mortality rate [1/day], {0.025}.

ZooMR = 0.025

# Large detritus remineralization rate N-fraction [1/day], {0.01}.

LDeRRN = 0.01

# Large detritus remineralization rate C-fraction [1/day].

LDeRRC = 0.01

# Coagulation rate: aggregation rate of SDeN + Phy => LDeN
# [1/day], {0.005}.

CoagR = 0.005

# Small detritus remineralization rate N-fraction [1/day], {0.03}.

SDeRRN = 0.03

# Small detritus remineralization rate C-fraction[1/day].

SDeRRC = 0.03

# River detritus remineralization rate N-fraction [1/day], {0.03}.

RDeRRN = 0.03

# River detritus remineralization rate N-fraction [1/day], {0.03}.

RDeRRC = 0.03

# Vertical sinking velocity for phytoplankton [m/day], {0.1}.

wPhy = 0.1

# Vertical sinking velocity for large detritus [m/day],
# {1.0}.

wLDet = 1.0

# Vertical sinking velocity for small detritus [m/day],
# {0.1}.

wSDet = 0.1

# CO2 partial pressure in the air (parts per million by volume),
# {377.0}.

pCO2air = 370.0

# ---------------------------------------------------------------------

def get_mu_max(temp, banas=False):
    """
    Max phytoplankton growth rate vs. temp
    Eppley (1972)
    
    Input:
    temp = pot. temperature [deg C]
    
    Output:
    mu_max = max growth rate [d-1]
    """
    
    if banas:
        mu_max = 1.7
    else:
        mu_0 = 0.59 # phytoplankton growth rate at 0 degC [d-1]
        mu_max = mu_0 * 1.066**temp
    
    return mu_max
    
def get_E(swrad0, z_rho, z_w, Chl, Phy, salt, banas=False):
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
    - and for compatibility with the Banas formulation:
    Phy = phytoplankton [mmol N m-3]
    salt = salinity [psu]
    
    Output:
    E = photosynthetically available radiation [W m-2]
    """
    dz = np.diff(z_w)
    N = len(Chl)
    if banas:
        AttSW_nb = 0.05 - (0.0065 * (salt - 32))
        AttPhy_nb = 0.03
        mean_Phy = np.zeros(N)
        for ii in range(N):
            this_dz = dz[ii:]
            this_dz[0] *= 0.5
            this_Phy = Phy[ii:]
            mean_Phy[ii] = np.sum(this_dz * this_Phy) / np.sum(this_dz)
        E = swrad0 * PARfrac * np.exp( z_rho * (AttSW_nb + AttPhy_nb*mean_Phy))
    else:
        mean_Chl = np.zeros(N)
        for ii in range(N):
            this_dz = dz[ii:]
            this_dz[0] *= 0.5
            this_Chl = Chl[ii:]
            mean_Chl[ii] = np.sum(this_dz * this_Chl) / np.sum(this_dz)
        E = swrad0 * PARfrac * np.exp( z_rho * (AttSW + AttChl*mean_Chl))
    return E
    
def get_f(E, mu_max, banas=False):
    """
    The photosynthesis-light relationship, Evans and Parslow (1985).
    
    Input:
    E = photosynthetically available radiation [W m-2]
    mu_max = max growth rate [d-1]
    
    Output:
    f = the P-I curve [dimensionless]
    """
    if banas:
        PhyIS_nb = 0.07
        f = PhyIS_nb * E / np.sqrt(mu_max**2 + (PhyIS_nb * E)**2)
    else:
        f = PhyIS * E / np.sqrt(mu_max**2 + (PhyIS * E)**2)
    return f
    
def get_Ing(Phy, Zoo, banas=False):
    """
    Hollings-type s-shaped grazing curve.
    
    Input:
    Phy = phytoplankton [mmol N m-3]
    
    Output:
    Ing = grazing rate [d-1] ("Ingestion" to match Banas terminology)
    """
    if banas:
        ZooGR_nb = 4.8
        K_Phy_nb = 9.0
        Ing = ZooGR_nb * (Phy * Zoo / (K_Phy_nb + Phy**2))
    else:
        Ing = ZooGR * (Phy * Zoo / (K_Phy + Phy**2))
    return Ing
    
def get_rho_Chl(mu, Phy, E, Chl):
    """
    Calculate the fraction of phytoplankton growth that goes into Chl synthesis.

    Input:
    mu = phytoplankton growth rate [d-1]
    Phy = phytoplankton [mmol N m-3]
    E = photosynthetically available radiation [W m-2]
    Chl = chlorophyll [mg Chl m-3]

    Output:
    rho_Chl = the fraction [dimensionless]
    """
    C_AtWt = 12 # Carbon atomic weight [g C / mol C]
    rho_Chl = PhyCN * C_AtWt * Chl2C_m * mu * Phy / (PhyIS * E * Chl)
    return rho_Chl
    
def get_Metab(Phy):
    """
    Calculate zooplankton metabolic loss rate.
    
    Input:
    Phy = phytoplankton [mmol N m-3]
    
    Output:
    Metab = metabolic loss rate [d-1]
    """
    Metab = ZooBM + ZooER * ZooAE_N * Phy**2 / (K_Phy + Phy**2)
    return Metab
    
def get_Coag(Phy, SDet, banas=False):
    """
    Calculate coagulation rate at which either Phy or SDet becomes LDet.

    Input:
    Phy = phytoplankton [mmol N m-3]
    SDet = small detritus [mmol N m-3]
    
    Output:
    Coag = coagulation rate [d-1]
    """
    if banas:
        CoagR_nb = 0.05
        Coag = CoagR_nb * Phy
    else:
        Coag = CoagR * (Phy + SDet)
    return Coag
    
def get_Nitri(E):
    """
    Calculate rate of nitrification (NH4 to NO3), which is light-limited.
    
    Input:
    E = photosynthetically available radiation [W m-2]
    
    Output:
    Nitr = nitrification rate [d-1]
    """
    Nitri = NitriR * (1 - np.maximum(0*E, ((E - I_thNH4) / (D_p5NH4 + E - I_thNH4))))
    return Nitri