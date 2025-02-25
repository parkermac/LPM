# Functions for harmonic analysis of tides

import utide

# list of frequencies to consider.  Sometimes we want to limit this
# because for shorter records utide can't separate nearby peaks
#hn_list = ['M2','S2','N2','O1','P1','K1']
hn_list = ['M2','S2','N2','O1','K1']

def get_harmonics(ser, lat):
    """
    Perform harmonic analysis on a time series, typically hourly.
    - ser is a Series with index t (datetime) and value z (SSH)
    """
    t = ser.index
    z = ser.to_numpy(dtype=float)
    h = utide.solve(t, z, v=None,
                 lat=lat,
                 nodal=False,
                 trend=False,
                 method='ols',
                 conf_int='linear',
                 Rayleigh_min=0.95)
    # h.aux.freq has units cyles/hour
    # so for f = h.aux.frq[h.name == 'M2'][0] we get
    # 1/f = 12.420601202671868 (hours per cycle)
    # h.A is amplitude (m), h.g is phase (degrees)
    return h

def get_AG(hn, h):
    """
    Convenience function for loading constituent info.
    We use the "[0]" because these are arrays and we want floats
    - hn is the name of the harmonic constituent, e.g. 'M2'
    - h is the output of get_harmonics
    """

    A = h.A[h.name==hn][0]
    G = h.g[h.name==hn][0]
    F = 24*h.aux.frq[h.name==hn][0] # cycles per day
    return A, G, F