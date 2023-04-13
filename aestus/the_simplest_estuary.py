"""
Code associated with a thought problem from 2023.04.11.

Q: Does mixing "control" the exchange flow?
"""

import numpy as np
import matplotlib.pyplot as plt

Socn = 30
qra = np.linspace(0,Socn,500) # Qr / alpha

DS = np.sqrt((qra/2)**2 + qra*Socn) - qra/2

DS_alt = 2*qra**(2/3) # a simple function that uses standard scaling for DS

plt.close('all')
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)

ax.plot(qra,DS,'-k',qra,DS_alt,'--k')
ax.grid(True)

plt.show()
