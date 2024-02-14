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

def airsea_oxygen(Oxy_surf, dtdays, Uwind=5, Vwind=5, temp_surf=10, salt_surf=25):
    """
    From:
    https://github.com/Jilian0717/LO_user/blob/main/LO_tracer_budget/get_DO_bgc_air_sea_1.py
    """

    #RW14_OXYGEN_SC = False
    #if RW14_OXYGEN_SC:   # cff2: s2/m
    #    cff2 = dtdays * 0.251 * 24 / 100  # 0.251: (cm/h)(m/s)^(-2), 
    #else:
    #    cff2 = dtdays * 0.31 * 24 / 100
    cff2_air = dtdays * 0.31 * 24 / 100

    #else: # Wanninkhof, 1992
    A_O2 = 1953.4; B_O2 = 128.0; C_O2 = 3.9918
    D_O2 = 0.050091; E_O2 = 0.0
    # Calculate O2 saturation concentration using Garcia and Gordon
    #  L and O (1992) formula, (EXP(AA) is in ml/l).
    OA0 = 2.00907       # Oxygen saturation coefficients
    OA1 = 3.22014;      OA2 = 4.05010;       OA3 = 4.94457
    OA4 = -0.256847;    OA5 = 3.88767;       OB0 = -0.00624523
    OB1 = -0.00737614;  OB2 = -0.0103410;    OB3 = -0.00817083
    OC0 = -0.000000488682    
    # Compute O2 transfer velocity: u10squared (u10 in m/s)
    u10squ = Uwind * Uwind + Vwind * Vwind  # ifdef BULK_FLUXES
    
    SchmidtN_Ox = A_O2 - temp_surf*(B_O2 - temp_surf*(C_O2 - temp_surf*(D_O2 - temp_surf*E_O2)))

    cff3 = cff2_air * u10squ * np.sqrt(660.0/SchmidtN_Ox)  # m
    TS = np.log((298.15-temp_surf)/(273.15+temp_surf))
    AA = OA0 + TS*(OA1+TS*(OA2+TS*(OA3+TS*(OA4+TS*OA5)))) + salt_surf*(OB0+TS*(OB1+TS*(OB2+TS*OB3))) + OC0*salt_surf*salt_surf
    # Convert from ml/l to mmol/m3
    # l2mol = 1000./22.3916   # liter to mol
    # O2satu = l2mol * np.exp(AA) # mmol/m3
    O2satu = 1000./22.3916 * np.exp(AA) # mmol/m3

    # Testing: this returns 300.67 with the default inputs
    # which seems reasonable.
    print('O2satu = %0.2f [mmol m-3]' % (O2satu))
    
    # O2 gas exchange
    # O2_Flux = cff3 * (O2satu-Oxy_surf)  # mmol O2/m2/hr ?
    # O2_Flux1 = O2_Flux * area * stat # mmol O2/hr 
    # Oxy_air_flux_sum.append(np.nansum(O2_Flux1)) # 

    # Oxy_air_flux_sum.append(np.nansum(cff3[jj,ii] * (O2satu[jj,ii]-Oxy_surf[jj,ii]) * area[jj,ii]))

    # This has units of 'mmol O2/hr' in Jilian's code, so I will want to convert it
    # to mmol O2/day for the biogeochemical code.
        