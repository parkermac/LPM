"""
Plot the results of net_flux_series.py
"""

from lo_tools import plotting_functions as pfun
import pandas as pd
from lo_tools import Lfun
import matplotlib.pyplot as plt

Ldir = Lfun.Lstart()

out_dir = Ldir['parent'] / 'LPM_output' / 'buoyancy_flux'
out_fn = out_dir / 'AI_highres.p'

df = pd.read_pickle(out_fn)

pfun.start_plot()

df.plot(subplots=True, grid=True)

plt.show()
pfun.end_plot()