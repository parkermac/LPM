import numpy as np

def update_v(v, E, dt):
    """
    In all the processes below we organize the backward-implicit integration
    around the variable that is being taken from (e.g. NO3 for phytoplankton growth).
    Hence we always write the "cff" term as: dt * rate factor * variable being taken from.
    This can sometimes be confusing because it is not how the terms are grouped
    when the equations are presented in the papers, but it works great for the numerics!

    v is a dict of the state variables, which can themselves be scalars or arrays [uM N]
    E is light [W m-2]
    dt is time step [d]

    The constants and algorithms reflect our current "x4b" model 2024_01
    """
    
    # phytoplankgon growth (Uptake)
    # light response curve
    mu_max = 1.7 # max growth rate [d-1]
    alpha = 0.07 # [(W m-2)-1 d-1]
    f = alpha * E / np.sqrt(mu_max**2 + (alpha * E)**2)
    # nutrient limitation curve and phytoplankton growth
    K3min = 0.1 # [uM]
    K4min = 0.1 # [uM]
    K3 = K3min + 2*np.sqrt(K3min * v['NO3'])
    K4 = K4min + 2*np.sqrt(K4min * v['NH4'])
    cff3 = dt * mu_max * f * (v['Phy'] / (K3 + v['NO3'])) * (K4 / (K4 + v['NH4']))
    cff4 = dt * mu_max * f * (v['Phy'] / (K4 + v['NH4']))
    v['NO3'] = v['NO3'] / (1 + cff3)
    v['NH4'] = v['NH4'] / (1 + cff4)
    v['Phy'] = v['Phy'] + cff3 * v['NO3'] + cff4 * v['NH4']
    
    # grazing by zooplankton (Ingestion)
    INGmax = 4.8 # [d-1]
    K = 9 # [uM^2]
    Ing = INGmax * (v['Phy'] * v['Zoo'] / (K + v['Phy']**2))
    beta = 0.3
    gamma = 0.5
    cff = dt * Ing
    v['Phy'] = v['Phy'] / (1 + cff)
    v['Zoo'] = v['Zoo'] + beta * cff * v['Phy']
    v['SDet'] = v['SDet'] + gamma * (1 - beta) * cff * v['Phy']
    v['NH4'] = v['NH4'] + (1 - gamma) * (1 - beta) * cff * v['Phy']
    
    # phytoplankton Mortality
    cff = dt * 0.1
    v['Phy'] = v['Phy'] / (1 + cff)
    v['SDet'] = v['SDet'] + cff * v['Phy']
    
    # zooplankton Mortality
    cff = dt * 2 * v['Zoo']
    v['Zoo'] = v['Zoo'] / (1 + cff)
    v['SDet'] = v['SDet'] + cff * v['Zoo']
    
    # coagulation
    Coag = 0.05 * v['SDet']
    cff = dt * Coag * v['SDet']
    v['SDet'] = v['SDet'] / (1 + cff)
    v['LDet'] = v['LDet'] + cff * v['SDet']
   
    # remineralization
    cffS = dt * 0.1
    v['SDet'] = v['SDet'] / (1 + cffS)
    v['NH4'] = v['NH4'] + cffS * v['SDet']
    cffL = dt * 0.1
    v['LDet'] = v['LDet'] / (1 + cffL)
    v['NH4'] = v['NH4'] + cffL * v['LDet']
    
    # nitrification
    Nitri = 0.05 # [d-1]
    cff = dt * Nitri
    v['NH4'] = v['NH4'] / (1 + cff)
    v['NO3'] = v['NO3'] + cff * v['NH4']
        
    return v