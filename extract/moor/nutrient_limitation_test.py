"""
Code to explore functional shapes associated with nutrient limitation.
"""

import numpy as np
import matplotlib.pyplot as plt


a = np.linspace(0,100,500)
b = np.linspace(0,100,500)
ab = a+b

f1 = a / (1 + a)
f2 = a / (1 + 2*np.sqrt(a) + a) # opt uptake
g1 = b / (1 + b)
g2 = b / (1 + 2*np.sqrt(b) + b) # opt uptake

h1 = f1 * (1 / (1 + b)) + g1
h2 = f2 * (1 / (1 + b)) + g2 # opt uptake
h3 = f2 * (1 / (1 + b)) + g1 # current
H1 = (ab) / (1 +  ab)
H2 = (ab) / (1 +  2*np.sqrt(ab) + ab) # opt uptake

plt.close('all')
fig = plt.figure(figsize=(11,7))
ax = fig.add_subplot(111)

ax.plot(ab,h1,'-r',label='standard')
ax.plot(ab,h2,'-b',label='opt uptake')
ax.plot(ab,h3,'-g',label='current')
ax.plot(ab,H1,'--r',label='target standard')
ax.plot(ab,H2,'--b',label='target opt uptake')

ax.legend()

plt.show()